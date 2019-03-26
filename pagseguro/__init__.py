# coding: utf-8
import logging
import requests

from .config import Config
from .utils import is_valid_email, is_valid_cpf, is_valid_cnpj
from .parsers import (PagSeguroNotificationResponse,
                      PagSeguroPreApprovalNotificationResponse,
                      PagSeguroPreApprovalCancel,
                      PagSeguroCheckoutSession,
                      PagSeguroPreApprovalPayment,
                      PagSeguroCheckoutResponse,
                      PagSeguroTransactionSearchResult,
                      PagSeguroPreApproval,
                      PagSeguroPreApprovalPlan,
                      PagSeguroPreApprovalSearch)

logger = logging.getLogger()


class PagSeguro(object):
    """ Pag Seguro V2 wrapper """

    PAC = 1
    SEDEX = 2
    NONE = 3

    def __init__(self, email, token, data=None, config=None):

        config = config or {}
        if not type(config) == dict:
            raise Exception('Malformed config dict param')

        if 'email_sender' in config:
            self.email_sender = config['email_sender']
        else:
            self.email_sender = ''

        self.config = Config(**config)

        self.data = {}
        self.data['email'] = email
        self.email = email
        self.data['token'] = token
        self.token = token

        if data and isinstance(data, dict):
            self.data.update(data)

        self.items = []
        self.sender = {}
        self.shipping = {}
        self._reference = ""
        self.extra_amount = None
        self.redirect_url = None
        self.notification_url = None
        self.abandon_url = None
        self.credit_card = {}
        self.pre_approval = {}
        self.checkout_session = None
        self.payment = {}

    def build_checkout_params(self, **kwargs):
        """ build a dict with params """
        params = kwargs or {}
        if self.sender:
            params['senderName'] = self.sender.get('name')[:50]
            params['senderAreaCode'] = self.sender.get('area_code')
            params['senderPhone'] = self.sender.get('phone')
            params['senderEmail'] = is_valid_email(self.sender.get('email'))
            params['senderCPF'] = is_valid_cpf(self.sender.get('cpf'))
            params['senderCNPJ'] = is_valid_cnpj(self.sender.get('cnpj'))
            params['senderBornDate'] = self.sender.get('born_date')
            params['senderHash'] = self.sender.get('hash')

        if self.config.USE_SHIPPING:
            if self.shipping:
                params['shippingType'] = self.shipping.get('type')
                params['shippingAddressStreet'] = self.shipping.get('street')[:80]
                params['shippingAddressNumber'] = self.shipping.get('number')[:20]
                params['shippingAddressComplement'] = self.shipping.get('complement')[:40]
                params['shippingAddressDistrict'] = self.shipping.get('district')[:60]
                params['shippingAddressPostalCode'] = self.shipping.get('postal_code')
                params['shippingAddressCity'] = self.shipping.get('city')[:60]
                params['shippingAddressState'] = self.shipping.get('state')
                params['shippingAddressCountry'] = self.shipping.get('country','BRA')
                if self.shipping.get('cost'):
                    params['shippingCost'] = self.shipping.get('cost')
        else:
            params['shippingAddressRequired'] = False
            params['shippingCost'] = 0.0

        if self.extra_amount:
            params['extraAmount'] = self.extra_amount

        params['reference'] = self.reference[:200]
        params['receiverEmail'] = self.data['email']

        if self.redirect_url:
            params['redirectURL'] = self.redirect_url[:255]

        if self.notification_url:
            params['notificationURL'] = self.notification_url

        if self.abandon_url:
            params['abandonURL'] = self.abandon_url

        for i, item in enumerate(self.items, 1):
            params['itemId%s' % i] = item.get('id')[:100]
            params['itemDescription%s' % i] = item.get('description')[:100]
            params['itemAmount%s' % i] = item.get('amount')
            params['itemQuantity%s' % i] = item.get('quantity')
            params['itemWeight%s' % i] = item.get('weight')
            params['itemShippingCost%s' % i] = item.get('shipping_cost')

        if self.payment:

            params['paymentMethod'] = self.payment.get('method')
            params['paymentMode'] = self.payment.get('mode')
            if self.payment.get('bank'):
                params['bankName'] = self.payment.get('bank')

        if self.credit_card:
            params['billingAddressCountry'] = 'BRA'

            credit_card_keys_map = [
                ('creditCardToken', 'credit_card_token'),
                ('installmentQuantity', 'installment_quantity'),
                ('installmentValue', 'installment_value'),
                ('noInterestInstallmentQuantity',
                 'no_interest_installment_quantity'),
                ('creditCardHolderName', 'card_holder_name'),
                ('creditCardHolderCPF', 'card_holder_cpf'),
                ('creditCardHolderBirthDate', 'card_holder_birth_date'),
                ('creditCardHolderAreaCode', 'card_holder_area_code'),
                ('creditCardHolderPhone', 'card_holder_phone'),
                ('billingAddressStreet', 'billing_address_street'),
                ('billingAddressNumber', 'billing_address_number'),
                ('billingAddressComplement', 'billing_address_complement'),
                ('billingAddressDistrict', 'billing_address_district'),
                ('billingAddressPostalCode', 'billing_address_postal_code'),
                ('billingAddressCity', 'billing_address_city'),
                ('billingAddressState', 'billing_address_state'),
            ]

            for key_to_set, key_to_get in credit_card_keys_map:
                params[key_to_set] = self.credit_card.get(key_to_get)

        self.data.update(params)
        self.clean_none_params()

    def build_pre_approval_subs_params(self, **kwargs):
        self.data = {
            "plan": self.code,
            "reference": self.reference,
            "sender":{
                "name": self.sender.get('name')[:50],
                "email": is_valid_email(self.sender.get('email')),
                "hash": self.sender.get('hash'),
                "phone":{
                    "areaCode": self.sender.get('area_code'),
                    "number": self.sender.get('phone')
                },
                "address":{
                    "street": self.shipping.get('street')[:80],
                    "number": self.shipping.get('number')[:20],
                    "complement": self.shipping.get('complement')[:40],
                    "district": self.shipping.get('district')[:60],
                    "city": self.shipping.get('city')[:60],
                    "state": self.shipping.get('state'),
                    "country": self.shipping.get('country', 'BRA'),
                    "postalCode": self.shipping.get('postal_code')
                },
                "documents":[
                    {
                        "type": "CPF",
                        "value": is_valid_cpf(self.sender.get('cpf'))
                    }
                ]
            },
            "paymentMethod":{
                "type":"CREDITCARD",
                "creditCard":{
                    "token": self.credit_card.get('credit_card_token'),
                    "holder":{
                        "name": self.credit_card.get('card_holder_name'),
                        "birthDate": self.credit_card.get('card_holder_birth_date'),
                        "documents":[
                            {
                                "type": "CPF",
                                "value": is_valid_cpf(self.credit_card.get('card_holder_cpf'))
                            }
                        ],
                        "billingAddress":{
                            "street": self.credit_card.get('billing_address_street')[:80],
                            "number": self.credit_card.get('billing_address_number')[:20],
                            "complement": self.credit_card.get('billing_address_complement')[:40],
                            "district": self.credit_card.get('billing_address_district')[:60],
                            "city": self.credit_card.get('billing_address_city')[:60],
                            "state": self.credit_card.get('billing_address_state'),
                            "country": self.credit_card.get('country', 'BRA'),
                            "postalCode": self.credit_card.get('billing_address_postal_code')
                        },
                        "phone":{
                            "areaCode": self.credit_card.get('card_holder_area_code'),
                            "number": self.credit_card.get('card_holder_phone')
                        }
                    }
                }
            }
        }


    def build_pre_approval_plan_params(self, **kwargs):
        params = kwargs or {}
        if self.pre_approval:
            params['preApprovalName'] = self.pre_approval.get('preApprovalName')
            params['preApprovalCharge'] = self.pre_approval.get('preApprovalCharge')
            params['preApprovalPeriod'] = self.pre_approval.get('preApprovalPeriod')
            params['preApprovalAmountPerPayment'] = self.pre_approval.get('preApprovalAmountPerPayment')
            params['preApprovalExpirationUnit'] = self.pre_approval.get('preApprovalExpirationUnit')
            params['preApprovalExpirationValue'] = self.pre_approval.get('preApprovalExpirationValue')
            params['preApprovalTrialPeriodDuration'] = self.pre_approval.get('preApprovalTrialPeriodDuration')
            params['preApprovalMembershipFee'] = self.pre_approval.get('preApprovalMembershipFee')
            params['maxUses'] = self.pre_approval.get('maxUses')

        self.data.update(params)
        self.clean_none_params()

    def clean_none_params(self):
        copy = dict(self.data)
        for k, v in list(copy.items()):
            if not v:
                del self.data[k]

    @property
    def reference_prefix(self):
        return self.config.REFERENCE_PREFIX or "%s"

    @reference_prefix.setter
    def reference_prefix(self, value):
        self.config.REFERENCE_PREFIX = (value or "") + "%s"

    @property
    def reference(self):
        return self.reference_prefix % self._reference

    @reference.setter
    def reference(self, value):
        if not isinstance(value, str):
            value = str(value)
        if value.startswith(self.reference_prefix):
            value = value[len(self.reference_prefix):]
        self._reference = value

    def get(self, url):
        """ do a get transaction """
        return requests.get(url, params=self.data, headers=self.config.HEADERS)

    def post(self, url):
        """ do a post request """
        #print(url)
        print(self.data)
        print(self.config.HEADERS)
        return requests.post(url, data=self.data, headers=self.config.HEADERS)

    def checkout(self, transparent=False, **kwargs):
        """ create a pagseguro checkout """
        self.data['currency'] = self.config.CURRENCY
        self.build_checkout_params(**kwargs)
        if transparent:
            self.response = self.post(url=self.config.TRANSPARENT_CHECKOUT_URL)
        else:
            self.response = self.post(url=self.config.CHECKOUT_URL)
        return PagSeguroCheckoutResponse(self.response.content, config=self.config)

    def transparent_checkout_session(self):
        response = self.post(url=self.config.SESSION_CHECKOUT_URL)
        return PagSeguroCheckoutSession(response.content,
                                        config=self.config).session_id

    def check_notification(self, code):
        """ check a notification by its code """
        self.response = self.get(url=self.config.NOTIFICATION_URL % code)
        return PagSeguroNotificationResponse(self.response.content, self.config)

    def check_pre_approval_notification(self, code):
        """ check a notification by its code """
        self.response = self.get(
            url=self.config.PRE_APPROVAL_NOTIFICATION_URL % code)
        return PagSeguroPreApprovalNotificationResponse(
            self.response.content, self.config)

    def pre_approval_create_plan(self, **kwargs):
        """ Create a plan """
        self.build_pre_approval_plan_params(**kwargs)
        self.response = self.post(url=self.config.PRE_APPROVAL_PLAN_URL)
        return PagSeguroPreApprovalPlan(self.response.content, self.config)

    def pre_approval_subs(self, **kwargs):
        """ Create a subscription """
        self.build_pre_approval_subs_params(**kwargs)
        self.response = requests.post(u'%s?email=%s&token=%s' % (self.config.PRE_APPROVAL_SUBS_URL, self.email, self.token),
            json=self.data, headers={'Accept': 'application/vnd.pagseguro.com.br.v3+json;charset=ISO-8859-1', 'Content-Type': 'application/json'})
        try:
            return self.response.json()
        except:
            return {'errors': {'0000': self.response.text, }, }

    def pre_approval_ask_payment(self, **kwargs):
        """ ask form a subscribe payment """
        self.build_pre_approval_payment_params(**kwargs)
        self.response = self.post(url=self.config.PRE_APPROVAL_PAYMENT_URL)
        return PagSeguroPreApprovalPayment(self.response.content, self.config)

    def pre_approval_cancel(self, code):
        """ cancel a subscribe """
        self.data = {
            "status": "SUSPENDED"
        }
        self.esponse = requests.put(u'%s?email=%s&token=%s' % ((self.config.PRE_APPROVAL_CANCEL_URL % code), self.email, self.token),
            json=self.data, headers={'Accept': 'application/vnd.pagseguro.com.br.v3+json;charset=ISO-8859-1', 'Content-Type': 'application/json'})

    def check_transaction(self, code):
        """ check a transaction by its code """
        self.response = self.get(url=self.config.TRANSACTION_URL % code)
        return PagSeguroNotificationResponse(self.response.content, self.config)

    def query_transactions(self, initial_date, final_date,
                           page=None,
                           max_results=None):
        """ query transaction by date range """
        last_page = False
        results = []
        while last_page is False:
            search_result = self._consume_query_transactions(
                initial_date, final_date, page, max_results)
            results.extend(search_result.transactions)
            if search_result.current_page is None or \
               search_result.total_pages is None or \
               search_result.current_page == search_result.total_pages:
                last_page = True
            else:
                page = search_result.current_page + 1

        return results

    def _consume_query_transactions(self, initial_date, final_date,
                                    page=None,
                                    max_results=None):
        querystring = {
            'initialDate': initial_date.strftime('%Y-%m-%dT%H:%M'),
            'finalDate': final_date.strftime('%Y-%m-%dT%H:%M'),
            'page': page,
            'maxPageResults': max_results,
        }
        self.data.update(querystring)
        self.clean_none_params()
        response = self.get(url=self.config.QUERY_TRANSACTION_URL)
        return PagSeguroTransactionSearchResult(response.content, self.config)

    def query_pre_approvals(self, initial_date, final_date, page=None,
                            max_results=None):
        """ query pre-approvals by date range """
        last_page = False
        results = []
        while last_page is False:
            search_result = self._consume_query_pre_approvals(
                initial_date, final_date, page, max_results)
            results.extend(search_result.pre_approvals)
            if search_result.current_page is None or \
               search_result.total_pages is None or \
               search_result.current_page == search_result.total_pages:
                last_page = True
            else:
                page = search_result.current_page + 1

        return results

    def _consume_query_pre_approvals(self, initial_date, final_date, page=None,
                                     max_results=None):
        querystring = {
            'initialDate': initial_date.strftime('%Y-%m-%dT%H:%M'),
            'finalDate': final_date.strftime('%Y-%m-%dT%H:%M'),
            'page': page,
            'maxPageResults': max_results,
        }

        self.data.update(querystring)
        self.clean_none_params()

        response = self.get(url=self.config.QUERY_PRE_APPROVAL_URL)
        return PagSeguroPreApprovalSearch(response.content, self.config)

    def query_pre_approvals_by_code(self, code):
        """ query pre-approvals by code """
        result = self._consume_query_pre_approvals_by_code(code)
        return result

    def _consume_query_pre_approvals_by_code(self, code):

        response = self.get(
            url='%s/%s' % (self.config.QUERY_PRE_APPROVAL_URL, code)
        )
        return PagSeguroPreApproval(response.content, self.config)

    def add_item(self, **kwargs):
        self.items.append(kwargs)