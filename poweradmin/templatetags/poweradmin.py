# coding: utf-8
from django.contrib.admin.views.main import PAGE_VAR
from django.template import Library
from datetime import datetime

from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = Library()
DOT = '.'

@register.filter(name='strptime')
def strptime(value, mash):
    return datetime.strptime(value, mash)


@register.inclusion_tag('admin/date_hierarchy.html', takes_context=True)
def power_date_hierarchy(context, cl):
    """
    Displays the date hierarchy for date drill-down functionality.
    """
    if cl.date_hierarchy:
        request = context.get('request')
        field_name = cl.date_hierarchy
        field = cl.opts.get_field(field_name)

        value__gte = value__lte = None
        if request.GET.get('%s__gte' % field_name):
            value__gte = datetime.strptime(request.GET.get('%s__gte' % field_name), "%Y-%m-%d")
        if request.GET.get('%s__lte' % field_name):
            value__lte = datetime.strptime(request.GET.get('%s__lte' % field_name), "%Y-%m-%d")

        return {
            'show': True,
            'field_name__gte': u'%s__gte' % field_name,
            'field_name__lte': u'%s__lte' % field_name,
            'field': field,
            'value__gte': value__gte,
            'value__lte': value__lte,
            'request': request,
        }

@register.simple_tag
def power_pagination(cl, i):
    if cl.multi_search_query:
        tag = '?'
        for k, v in cl.multi_search_query.items():
            tag += '%s=%s&' % (k, v)

        if i == DOT:
            return '... '
        elif i == cl.page_num:
            return format_html('<span class="this-page">{}</span> ', i + 1)
        else:
            return format_html('<a href="{}p={}"{}>{}</a> ',
                               tag,
                               i,
                               mark_safe(' class="end"' if i == cl.paginator.num_pages - 1 else ''),
                               i + 1)
    else:
        """
           Generates an individual page index link in a paginated list.
           """
        if i == DOT:
            return '... '
        elif i == cl.page_num:
            return format_html('<span class="this-page">{}</span> ', i + 1)
        else:
            return format_html('<a href="{}"{}>{}</a> ',
                               cl.get_query_string({PAGE_VAR: i}),
                               mark_safe(' class="end"' if i == cl.paginator.num_pages - 1 else ''),
                               i + 1)