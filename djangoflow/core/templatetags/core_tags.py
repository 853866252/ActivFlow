"""Template Tags"""

import itertools

from collections import OrderedDict
from django import template

from djangoflow.core.helpers import discover

register = template.Library()


def get_entity_data(instance, app, option):
    """Prepares the fields/data for display"""
    model = type(instance)
    field_config = discover()[app][model.__name__]

    def compute(field_config):
        for field_name in field_config:
            if option in field_config[field_name]:
                yield field_name

    return OrderedDict([(model().class_meta.get_field(
        field_name).verbose_name, getattr(
            instance, field_name)) for field_name in itertools.islice(
                compute(field_config), len(field_config))])


@register.filter(is_safe=True)
def label_with_class(value, arg):
    """Style adjustments"""
    return value.label_tag(attrs={'class': arg})


@register.assignment_tag(takes_context=True)
def model_field_values(context, option):
    """Returns pair for field/values for display"""
    instance = context['object']
    app = context['app_title']

    return get_entity_data(instance, app, option)


@register.assignment_tag(takes_context=True)
def entity_preview(context):
    """Returns pair for field/values for preview"""
    _parent = {}
    instances = context['objects']
    app = context['app_title']

    for instance in instances:
        _parent[instance.id] = get_entity_data(
            instance, app, 'preview')

    return _parent


@register.assignment_tag
def model_label_for_search(obj):
    """Returns entity name"""
    return type(obj).__name__


@register.simple_tag
def activity_title(ref, app):
    """Returns entity name"""
    from importlib import import_module

    from django.apps import apps

    return import_module(
        '{}.flow'.format(apps.get_app_config(app).name)
    ).FLOW[ref]['model']().title


@register.assignment_tag
def activity_identifier(task):
    """Returns activity identifier"""
    activity_identifier = task.activity

    return activity_identifier if activity_identifier else None
