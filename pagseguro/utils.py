# coding: utf-8
import re
import collections
import arrow

from .exceptions import PagSeguroValidationError

def parse_date(date_str):
    return arrow.get(date_str).datetime

# Validators
EMPTY_VALUES = (None, '', [], (), {},)

def is_valid_email(value):
    user_regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*$"
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013'
        r"""\014\016-\177])*"$)""", re.IGNORECASE)
    domain_regex = re.compile(
        r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}|'
        r'[A-Z0-9-]{2,})$|^\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|'
        r'2[0-4]\d|[0-1]?\d?\d)){3}\]$', re.IGNORECASE)
    domain_whitelist = ['localhost']

    if not value or '@' not in value:
        raise PagSeguroValidationError(u'Email inválido')

    user_part, domain_part = value.rsplit('@', 1)

    if not user_regex.match(user_part):
        raise PagSeguroValidationError(u'Email inválido')

    if (domain_part not in domain_whitelist and
            not domain_regex.match(domain_part)):
        # Try for possible IDN domain-part
        try:
            domain_part = domain_part.encode('idna').decode('ascii')
            if not domain_regex.match(domain_part):
                raise PagSeguroValidationError(u'Email inválido')
            else:
                return value
        except UnicodeError:
            pass
        raise PagSeguroValidationError(u'Email inválido')
    return value


def DV_maker(v):
    if v >= 2:
        return 11 - v
    return 0


def is_valid_cpf(value):
    error_messages = {
        'invalid': u"CPF Inválido",
        'max_digits': (u"CPF possui 11 dígitos (somente números) ou 14"
                       u" (com pontos e hífen)"),
        'digits_only': (u"Digite um CPF com apenas números ou com ponto e "
                        u"hífen"),
    }

    if value in EMPTY_VALUES:
        return u''
    orig_value = value[:]
    if not value.isdigit():
        value = re.sub("[-\.]", "", value)
    try:
        int(value)
    except ValueError:
        raise PagSeguroValidationError(error_messages['digits_only'])
    if len(value) != 11:
        raise PagSeguroValidationError(error_messages['max_digits'])
    orig_dv = value[-2:]

    new_1dv = sum([i * int(value[idx]) for idx, i in enumerate(range(10, 1, -
    1))])
    new_1dv = DV_maker(new_1dv % 11)
    value = value[:-2] + str(new_1dv) + value[-1]
    new_2dv = sum([i * int(value[idx]) for idx, i in enumerate(range(11, 1, -
    1))])
    new_2dv = DV_maker(new_2dv % 11)
    value = value[:-1] + str(new_2dv)
    if value[-2:] != orig_dv:
        raise PagSeguroValidationError(error_messages['invalid'])

    return orig_value


def is_valid_cnpj(value):
    error_messages = {
        'invalid': u"CNPJ Inválido",
        'max_digits': (u"CNPJ possui 14 dígitos (somente números) ou 14"
                       u" (com pontos e hífen)"),
        'digits_only': (
            u"Digite um CNPJ com apenas números ou com ponto, barra "
            u"hífen"),
    }

    if value in EMPTY_VALUES:
        return u''
    if not value.isdigit():
        value = re.sub("[-/\.]", "", value)
    orig_value = value[:]
    try:
        int(value)
    except ValueError:
        raise PagSeguroValidationError(error_messages['digits_only'])
    if len(value) != 14:
        raise PagSeguroValidationError(error_messages['max_digits'])

    orig_dv = value[-2:]

    new_1dv = sum([i * int(value[idx]) for idx, i in enumerate(range(
        5, 1, -1) + range(9, 1, -1))])
    new_1dv = DV_maker(new_1dv % 11)
    value = value[:-2] + str(new_1dv) + value[-1]
    new_2dv = sum([i * int(value[idx]) for idx, i in enumerate(range(
        6, 1, -1) + range(9, 1, -1))])
    new_2dv = DV_maker(new_2dv % 11)
    value = value[:-1] + str(new_2dv)
    if value[-2:] != orig_dv:
        raise PagSeguroValidationError(error_messages['invalid'])

    return orig_value


def create_error_message(errors):
    code_errors = {
        '5003': u'Falha de comunicação com a instituição financeira.',
        '10000': u'Bandeira do cartão inválido.',
        '10001': u'Numeração do cartão de crédito inválida.',
        '10002': u'Formato de data inválida.',
        '10003': u'Campo de segurança inválido.',
        '10004': u'Campo de segurança é obrigatório.',
        '10006': u'Campo de segurança inválido.',
        '53004': u'Itens de quantidade inválida.',
        '53005': u'Moeda é obrigatório.',
        '53006': u'Valor inválido de moeda.',
        '53007': u'Comprimento inválido de referência.',
        '53008': u'Tamnho inválido da NotificationURL.',
        '53009': u'NotificationURL inválido.',
        '53010': u'É obrigatório o e-mail do remetente.',
        '53011': u'Email do remetente inválido.',
        '53012': u'Email inválido inválido.',
        '53013': u'O nome do remetente é obrigatório.',
        '53014': u'Tamanho inválido do nome do remetente.',
        '53015': u'Nome do remetente inválido.',
        '53017': u'CPF do remetente inválido.',
        '53018': u'Código de área do remetente é obrigatório.',
        '53019': u'Código de área do remetente inválido.',
        '53020': u'O telefone do remetente é obrigatório.',
        '53021': u'Telefone do remetente inválido.',
        '53022': u'O endereço postal é obrigatório.',
        '53023': u'Código postal do endereço de entrega inválido.',
        '53024': u'Endereço de remessa é obrigatório.',
        '53025': u'Tamanho inválido do endereço de entrega.',
        '53026': u'Número de endereço de remessa é obrigatório.',
        '53027': u'Tamanho inválido do número de endereço de entrega.',
        '53028': u'Tamanho inválido do complemento do endereço de remessa.',
        '53029': u'Distrito do endereço de entrega é obrigatório.',
        '53030': u'Tamanho inválido do distrito do endereço de entrega.',
        '53031': u'A cidade de endereço de entrega é obrigatório.',
        '53032': u'Tamanho inválido do cidade do endereço de entrega.',
        '53033': u'O endereço do remetente é obrigatório.',
        '53034': u'Valor do endereço do endereço de envio inválido.',
        '53035': u'País de endereço de remessa.',
        '53036': u'Tamanho inválido do país do endereço de entrega.',
        '53037': u'Cartão de crédito é obrigatório.',
        '53038': u'Quantidade de parcela é obrigatório.',
        '53039': u'Quantidade de parcela valor inválido.',
        '53040': u'O valor da parcela é obrigatório.',
        '53041': u'Valor de valor de parcelamento inválido.',
        '53042': u'O nome do titular do cartão de crédito é obrigatório.',
        '53043': u'Tamanho inválido do Nome do titular do cartão de crédito.',
        '53044': u'Nome do titular do cartão de crédito valor inválido.',
        '53045': u'Titular do cartão de crédito cpf é obrigatório.',
        '53046': u'Titular do cartão de crédito cpf valor inválido.',
        '53047': u'Data de nascimento do titular do cartão de crédito é obrigatório.',
        '53048': u'Titular do cartão de crédito data de nascimento valor inválido.',
        '53049': u'O código de área do titular do cartão de crédito é obrigatório.',
        '53050': u'Código de área do titular do cartão de crédito Valor inválido.',
        '53051': u'Cartão de crédito é obrigatório.',
        '53052': u'Titular do cartão de crédito inválido valor do telefone.',
        '53053': u'O endereço postal é obrigatório.',
        '53054': u'Endereço de faturamento código postal valor inválido.',
        '53055': u'A rua de endereço de faturamento é obrigatório.',
        '53056': u'Tamanho inválido do Endereço de faturamento rua.',
        '53057': u'Número de endereço de faturamento é obrigatório.',
        '53058': u'Tamanho inválido do Número de endereço de faturamento.',
        '53059': u'Tamanho inválido do Endereço de faturamento complementar.',
        '53060': u'Endereço de faturamento distrito é obrigatório.',
        '53061': u'Tamanho inválido do Endereço de faturamento distrito.',
        '53062': u'Cidade de endereço de faturamento é obrigatório.',
        '53063': u'Tamanho inválido do Endereço de faturamento cidade.',
        '53064': u'O estado do endereço de faturamento é obrigatório.',
        '53065': u'Estado de endereço de faturamento valor inválido.',
        '53066': u'País de endereço de faturamento é obrigatório.',
        '53067': u'Tamanho inválido do Endereço de faturamento país.',
        '53068': u'Comprimento do destinatário do email inválido.',
        '53069': u'Valor inválido do e-mail do destinatário.',
        '53070': u'Item id é obrigatório.',
        '53071': u'Tamanho inválido do ID do artigo.',
        '53072': u'A descrição do item é obrigatório.',
        '53073': u'Tamanho inválido do Descrição do item.',
        '53074': u'Item quantidade é obrigatório.',
        '53075': u'Quantidade do item fora do intervalo.',
        '53076': u'Quantidade de item valor inválido.',
        '53077': u'Item quantidade é obrigatório.',
        '53078': u'Valor do item padrão inválido.',
        '53079': u'Quantidade do item fora do intervalo.',
        '53081': u'O remetente está relacionado ao receptor.',
        '53084': u'Receptor inválido., verifique o status da conta do receptor e se é uma conta do vendedor.',
        '53085': u'Método de pagamento indisponível.',
        '53086': u'Total do carrinho fora do intervalo.',
        '53087': u'Dados de cartão de crédito inválidos.',
        '53091': u'Hash do remetente inválido.',
        '53092': u'A marca de cartão de crédito não é aceite.',
        '53095': u'Tipo de envio padrão inválido.',
        '53096': u'Custo de transporte padrão inválido.',
        '53097': u'Custo de envio fora do intervalo.',
        '53098': u'O valor total do carrinho é negativo.',
        '53099': u'Valor extra padrão inválido.',
        '53101': u'Modo de pagamento inválido valor, valores válidos são padrão e gateway.',
        '53102': u'Valor de pagamento inválido, valores válidos são creditCard, boleto e eft.',
        '53104': u'O custo de transporte foi fornecido, o endereço do transporte deve estar completo.',
        '53105': u'Informações do remetente foram fornecidas, e-mail deve ser fornecido também.',
        '53106': u'Titular do cartão de crédito está incompleta.',
        '53109': u'As informações de endereço de entrega foram fornecidas, o e-mail do remetente também deve ser fornecido.',
        '53110': u'Eft banco é obrigatório.',
        '53111': u'Eft bank não é aceito.',
        '53115': u'Data de nascimento do remetente valor inválido.',
        '53117': u'Remetente cnpj valor inválido.',
        '53122': u'Remetente email domínio inválido. Você deve usar um email @ sandbox.pagseguro.com.br',
        '53140': u'Quantidade da parcela fora do intervalo. O valor deve ser maior que zero.',
        '53141': u'O remetente está bloqueado.',
        '53142': u'Cartão de crédito token inválido.',
    }
    if type(errors) == collections.OrderedDict:
        errors = [dict(errors), ]
    else:
        errors = list(errors)

    mensagens = []
    for error in errors:
        try:
            error_code = dict(error).get('code')
            if error_code == '53021':
                mensagens.append(u'%s <a href="%s">Reveja seus dados cadastrais</a>' % (
                code_errors[error_code], reverse('cadastro')))
            else:
                mensagens.append(u'%s (%s)' % (code_errors[error_code], error_code))
        except:
            mensagens.append(u'%s' % error)
    return mensagens
