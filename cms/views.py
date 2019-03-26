# coding: utf-8
from django.views.generic import DetailView, TemplateView, View, FormView
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponsePermanentRedirect, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.db.models import Q

import json as simplejson


# password_reset_confirm
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.template.response import TemplateResponse
from django.utils.http import base36_to_int
from django.contrib.auth import login as auth_login, authenticate

from .models import Article, Section, URLMigrate, FileDownload, Recurso, Permissao, \
    GroupType, GroupItem, EmailAgendado
from .forms import ArticleCommentForm, UpdateForm, CMSUserCreationForm

import mimetypes, os
from util.stdlib import server_status


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class UpdateView(LoginRequiredMixin, View):
    title = u'Atualizar PowerCMS'
    form_class = UpdateForm
    template_name='admin/cms/update.html'

    def post(self, *args, **kwargs):
        form = self.form_class(self.request.POST)
        if form.is_valid():
            version = form.cleaned_data.get('version')
            os.system('git pull')
            if version:
                os.system('git checkout %s' % version)
            os.system("%(PROJECT_DIR)s/../../bin/python %(PROJECT_DIR)s/../manage.py syncdb --settings=powercms.settings.production" % {
                'PROJECT_DIR': settings.PROJECT_DIR,
            })
            os.system("%(PROJECT_DIR)s/../../bin/python %(PROJECT_DIR)s/../manage.py migrate --settings=powercms.settings.production" % {
                'PROJECT_DIR': settings.PROJECT_DIR,
            })
            os.system("%(PROJECT_DIR)s/../../bin/python %(PROJECT_DIR)s/../manage.py syncdb --all --settings=powercms.settings.production" % {
                'PROJECT_DIR': settings.PROJECT_DIR,
            })
            os.popen('supervisorctl restart %s' % settings.PROJECT_DIR.split('/')[-2])
            messages.info(self.request, u'Sistema atualizado com sucesso!')
        return render(self.request, self.template_name, {
            'form': form,
            'title': self.title,
        })

    def get(self, *args, **kwargs):
        form = self.form_class()
        return render(self.request, self.template_name, {
            'form': form,
            'title': self.title,
        })


class ArticleDetailView(DetailView):
    model = Article
    form = ArticleCommentForm

    def get_template_names(self):
        templates = []
        for section in self.object.sections.all():
            templates.append('%s/article.html' % section.slug)
            templates.append('%s/%s.html' % (section.slug, self.object.slug,))
        templates.append('article/%s.html' % self.object.slug)
        templates.append('article.html')
        return templates

    def get_context_data(self, **kwargs):
        form = self.form()
        if self.request.method == 'POST':
            form = self.form(self.request.POST, initial={'article': self.object, })
            if form.is_valid() and self.object.allow_comments in ('A', 'P'):
                form.instance.article = self.object
                form.save()
                form.sendemail()
                form = self.form()
                messages.info(self.request, u'Comentário enviado!')
            else:
                messages.error(self.request, u'Corrija os erros abaixo!')
        return {
            'article': self.object,
            'form': form,
        }

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get(self, *args, **kwargs):
        response = super(ArticleDetailView, self).get(*args, **kwargs)
        # Redirecionar para a home se: A sessão tem permissão e o usuário não está nesse grupo
        if not self.object.have_perm(self.request.user):
            messages.error(self.request, u'Você não tem permissão para acessar esse artigo!')
            return HttpResponseRedirect(reverse('home'))
        self.object.views += 1
        self.object.save()
        return response


class SectionDetailView(DetailView):
    model = Section

    def get_template_names(self):
        if self.object.template:
            return [self.object.template, ]
        return [
            'section/%s.html' % self.object.slug,
            '%s/section.html' % self.object.slug,
            'section.html',
        ]

    def get_context_data(self, **kwargs):
        articles_list = []
        for article in self.object.get_articles():
            if article.have_perm(self.request.user):
                articles_list.append(article)

        paginator = Paginator(articles_list, 5)

        page = self.request.GET.get('page')
        try:
            articles = paginator.page(page)
        except PageNotAnInteger:
            articles = paginator.page(1)
        except EmptyPage:
            articles = paginator.page(paginator.num_pages)
        return {
            'section': self.object,
            'articles': articles,
        }


    def get(self, *args, **kwargs):
        response = super(SectionDetailView, self).get(*args, **kwargs)
        # Redirecionar para a home se: A sessão tem permissão e o usuário não está nesse grupo
        if not self.object.have_perm(self.request.user):
            messages.error(self.request, u'Você não tem permissão para acessar essa sessão!')
            return HttpResponseRedirect(reverse('home'))
        self.object.views += 1
        self.object.save()
        return response


class HomeView(TemplateView):
    template_name = 'home.html'


class LinkConversionView(View):
    def get(self, request, *args, **kwargs):
        if not 'next' in request.GET:
            raise Http404

        if 'section_slug' in kwargs:
            section = get_object_or_404(Section, slug=kwargs.get('section_slug'))
            section.conversions += 1
            section.save()
        elif 'article_slug' in kwargs:
            article = get_object_or_404(Article, slug=kwargs.get('article_slug'))
            article.conversions += 1
            article.save()

        next = request.GET.get('next')
        if not 'http' in next:
            next = 'http://%s' % next
        return redirect(next)


class URLMigrateView(View):
    def get(self, request, old_url, *args, **kwargs):
        url = get_object_or_404(URLMigrate, old_url=old_url)
        url.views += 1
        url.save()
        if url.redirect_type == 'M':
            return HttpResponsePermanentRedirect(url.new_url)
        return HttpResponseRedirect(url.new_url)


class FileDownloadView(View):
    def get(self, request, file_uuid, *args, **kwargs):
        file_download = get_object_or_404(FileDownload, uuid=file_uuid)
        if file_download.is_expired():
            raise Http404()

        file_download.count += 1
        file_download.save()

        mimetype = mimetypes.guess_type(file_download.file.path)[0]
        return HttpResponse(file_download.file.read(), content_type=mimetype)


class SearchView(TemplateView):
    template_name = 'search.html'

    def get_context_data(self, **kwargs):
        q = self.request.GET.get('q')
        results_list = []
        if q:
            articles_list = Article.objects.filter(
                is_active=True
            ).filter(
                Q(title__icontains=q) |
                Q(header__icontains=q) |
                Q(content__icontains=q) |
                Q(keywords__icontains=q)
            ).distinct()
            for article in articles_list:
                if article.have_perm(self.request.user):
                    results_list.append({
                        'title': article.title,
                        'object': article,
                    })
            results_list = sorted(results_list, key=lambda k: k['title'])

        paginator = Paginator(results_list, 5)
        page = self.request.GET.get('page')
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)
        return {
            'q': q,
            'results': results,
        }


class RobotsView(View):
    def get(self, request, *args, **kwargs):
        robots = Recurso.objects.get_or_create(recurso='ROBOTS')[0]
        if robots.ativo:
            return HttpResponse(u'User-agent: *\nAllow: *', content_type='text/plain')
        return HttpResponse(u'User-agent: *\nDisallow: *', content_type='text/plain')


class SignupView(FormView):
    form_class = CMSUserCreationForm
    template_name = 'auth/signup.html'
    template_name_done = 'auth/signup_done.html'

    def form_valid(self, form):
        form.save()
        form = self.form_class()
        return self.response_class(
            request=self.request,
            template=self.template_name_done,
            context=self.get_context_data(form=form),
        )



@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request, uidb36=None, token=None,
                           template_name='auth/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect='/',
                           current_app=None, extra_context=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    assert uidb36 is not None and token is not None # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('django.contrib.auth.views.password_reset_complete')
    try:
        uid_int = base36_to_int(uidb36)
        user = User.objects.get(id=uid_int)
    except (ValueError, User.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                user = authenticate(username=user.username, password=form.cleaned_data['new_password1'])
                auth_login(request, user)
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(None)
    else:
        validlink = False
        form = None
    context = {
        'form': form,
        'validlink': validlink,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


def signup_filter(request, grouptype_id, groupitem_id):
    pai = get_object_or_404(GroupItem, pk=groupitem_id)
    grouptype = get_object_or_404(GroupType, pk=grouptype_id)

    results = []
    pai_sessoes_ids = Permissao.objects.filter(group=pai.group).values_list('section', flat=True)
    for item in grouptype.groupitem_set.all():
        if Permissao.objects.filter(group=item.group, section__pk__in=pai_sessoes_ids).exists():
            results.append(item)

    result = []
    for item in results:
        result.append({'pk': item.pk, 'display': item})
    json = simplejson.dumps(result)
    return HttpResponse(json, mimetype='application/json')

def status(request):
    json = server_status()
    status_email = 0  # Enabled
    if EmailAgendado.objects.latest('pk').status == 'E':
        status_email = 1  # Com erro
    elif not Recurso.objects.get_or_create(recurso='EMAIL')[0].ativo:
        status_email = 2  # Disable
    json['mail'] = {
        'Available': status_email
    }
    return HttpResponse(simplejson.dumps(json), content_type="application/json")