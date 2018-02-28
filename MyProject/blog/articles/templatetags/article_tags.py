import markdown2
from django import template
from django.utils.safestring import mark_safe

from ..models import Article

register = template.Library()


@register.simple_tag
def total_articles():
    return Article.objects.filter(status='publish').count()


@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown2.markdown(text))
