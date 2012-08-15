import re

from django import forms

class ArrayField(forms.Field):
    def __init__(self, **kwargs):
        super(ArrayField, self).__init__(**kwargs)

    def prepare_value(self, value):
        if isinstance(value, (list, tuple)):
            return re.sub(r'\[|\]','',str(value))
        return value
