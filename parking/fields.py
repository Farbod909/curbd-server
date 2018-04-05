from django import forms
from django.contrib.postgres.fields import ArrayField
from rest_framework.serializers import ListField, HyperlinkedRelatedField

from .models import Car


class ChoiceArrayField(ArrayField):
    """
    A field that allows us to store an array of choices.

    Uses Django 1.9's postgres ArrayField
    and a MultipleChoiceField for its formfield.

    Usage:

        choices = ChoiceArrayField(models.CharField(max_length=...,
                                                    choices=(...,)),
                                   default=[...])
    """

    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.MultipleChoiceField,
            'choices': self.base_field.choices,
            'widget': forms.CheckboxSelectMultiple,
        }
        defaults.update(kwargs)
        # Skip our parent's formfield implementation completely as we don't
        # care for it.
        # pylint:disable=bad-super-call
        return super(ArrayField, self).formfield(**defaults)


class StringArrayField(ListField):
    """
    String representation of an array field.
    """
    def to_representation(self, obj):
        obj = super().to_representation(obj)
        # convert list to string
        return ", ".join([str(element) for element in obj])

    def to_internal_value(self, data):
        data = data[0].split(", ")  # convert string to list
        return super().to_internal_value(data)


class CarField(HyperlinkedRelatedField):
    """
    Field that limits the queryset of the cars to the cars
    owned by the current user
    """
    view_name = 'car-detail'

    def get_queryset(self):
        return Car.objects.filter(customer__user=self.context['request'].user)

