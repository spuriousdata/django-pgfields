import re

from psycopg2.extensions import adapt
from django.db import models

try:
    from south.modelsinspector import add_introspection_rules as addrule
except ImportError:
    def addrule(a,b):
        pass

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
            dbval = self.stringify(value)
            return "'{%s}'" % dbval
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
addrule([], ['pgfields\.arrays\.ArrayField'])


class CharArrayField(ArrayField):
    description = "PostgreSQL char[]"
    field_type = "char"
    subtype = str

    def stringify(self, value):
        quoted = [str(adapt(x).getquoted()) for x in value]
        return ",".join(quoted)
addrule([], ['pgfields\.arrays\.CharArrayField'])

class VarcharArrayField(CharArrayField):
    description = "PostgreSQL varchar[]"
    field_type = "varchar"
addrule([], ['pgfields\.arrays\.VarcharArrayField'])

class TextArrayField(CharArrayField):
    description = "PostgreSQL text[]"
    field_type = "text"
addrule([], ['pgfields\.arrays\.TextArrayField'])

class NumericArrayField(ArrayField):
    description = "PostgreSQL numeric[]"
    field_type = "numeric"
    subtype = float

    def stringify(self, value):
        return ','.join([str(x) for x in value])
addrule([], ['pgfields\.arrays\.NumericArrayField'])

class IntegerArrayField(NumericArrayField):
    description = "PostgreSQL integer[]"
    field_type = "integer"
    subtype = float
addrule([], ['pgfields\.arrays\.IntegerArrayField'])

class FloatArrayField(NumericArrayField):
    description = "PostgreSQL float[]"
    field_type = "float"
    subtype = float
addrule([], ['pgfields\.arrays\.FloatArrayField'])
