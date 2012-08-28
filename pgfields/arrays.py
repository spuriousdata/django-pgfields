import re

from psycopg2.extensions import adapt
from django.db import models

class ArrayField(models.Field):
    description = "PostgreSQL array type"
    field_type = ""
    subtype = type(None)
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(ArrayField, self).__init__(*args, **kwargs)

    def stringify(self, value):
        raise NotImplemented, "Must be overridden by subclass"

    def db_type(self, connection):
        size = "(%d)" % self.max_length if self.max_length else ""
        return "%s%s[]" % (self.field_type, size)

    def get_prep_value(self, value):
        """
        Convert python type to sql
        """
        if isinstance(value, list):
            return value
        elif isinstance(value, (str, unicode)):
            if not value:
                return None
            return value

    def to_python(self, value):
        """
        Convert value to python type
        """
        if isinstance(value, list):
            return value
        elif isinstance(value, (str, unicode)):
            if not value:
                return None
            value = re.sub(r'\{|\}', '', value).split(',')
            return map(lambda x: self.subtype(x), value)

class CharArrayField(ArrayField):
    description = "PostgreSQL char[]"
    field_type = "char"
    subtype = unicode

    def stringify(self, value):
        quoted = [adapt(x.encode('utf8')).getquoted() for x in value]
        return ",".join(quoted)

class VarcharArrayField(CharArrayField):
    description = "PostgreSQL varchar[]"
    field_type = "varchar"

class TextArrayField(CharArrayField):
    description = "PostgreSQL text[]"
    field_type = "text"

class NumericArrayField(ArrayField):
    description = "PostgreSQL numeric[]"
    field_type = "numeric"
    subtype = float

    def stringify(self, value):
        return ','.join([str(x) for x in value])

class IntegerArrayField(NumericArrayField):
    description = "PostgreSQL integer[]"
    field_type = "integer"
    subtype = float

class FloatArrayField(NumericArrayField):
    description = "PostgreSQL float[]"
    field_type = "float"
    subtype = float
