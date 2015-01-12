import hashlib
import uuid

from psycopg2.extensions import adapt
from psycopg2.extras import register_uuid
from django.db import models

from pgfields.utils import addrule, register_initializer

from django.db import connection, transaction
@transaction.autocommit()
def init_enums(sender, **kwargs):
    cursor = connection.cursor()
    for name, sql in _typesql.items():
        cursor.execute("SELECT EXISTS(SELECT typname FROM pg_type WHERE typname=%s);", [name])
        result = cursor.fetchone()
        if not result[0]:
            cursor.execute(sql)
            transaction.commit_unless_managed()
register_initializer(init_enums)

def init_uuid(sender, **kwargs):
    register_uuid()

_typesql = {}

class EnumField(models.Field):
    description = "PostgreSQL enum type"
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        global _typesql
        self.enumeration = kwargs.pop('enumeration')
        self.type_name = kwargs.pop('type_name',
                                   'enum_'+hashlib.md5('|'.join(self.enumeration)).hexdigest())
        kwargs['choices'] = [(v,v) for v in self.enumeration]
        try:
            kwargs['default'] = str(adapt(kwargs['default']).getquoted())
        except KeyError:
            pass
        _typesql[self.type_name] = self.create_type()
        super(EnumField, self).__init__(*args, **kwargs)
        
    def deconstruct(self):
        name, path, args, kwargs = super(EnumField, self).deconstruct()
        kwargs['enumeration'] = self.enumeration
        kwargs['type_name'] = self.type_name
        del kwargs['choices']
        try:
            del kwargs['default']
        except KeyError:
            pass
        return name, path, args, kwargs

    def db_type(self, connection):
        return self.type_name

    def create_type(self):
        return "CREATE TYPE %s as ENUM (%s)" % (
            self.type_name, ','.join(str(adapt(v).getquoted()) for v in self.enumeration)
        )

addrule([
    (
        [EnumField],
        [],
        {
            'enumeration':['enumeration', {}],
            'type_name':['type_name', {}],
        },
    ),
], ['^pgfields\.basic\.EnumField'])

class UUIDField(models.Field):
    description = "PostgreSQL UUID type"
    __metaclass__ = models.SubfieldBase
    __uuid_version_default = 4

    def __init__(self, *args, **kwargs):
        self.uuid_version = kwargs.pop('uuid_version', UUIDField.__uuid_version_default)
        # GAH! Can't do this, django caches the default value as a static
        # string
        #kwargs['default'] = getattr(uuid, "uuid%d" % self.uuid_version)()
        super(UUIDField, self).__init__(*args, **kwargs)
        
    def deconstruct(self):
        name, path, args, kwargs = super(UUIDField, self).deconstruct()
        if self.uuid_version != UUIDField.__uuid_version_default:
            kwargs['uuid_version'] = self.uuid_version
        return name, path, args, kwargs

    def get_prep_value(self, value):
        if value == '':
            value = getattr(uuid, "uuid%d" % self.uuid_version)()
        if type(value) == str and value.find('-') == -1:
            value = uuid.UUID(value)
        return str(value)

    def to_python(self, value):
        return str(value)

    def db_type(self, connection):
        return 'UUID'

    def pre_save(self, model_instance, add):
        value = super(UUIDField, self).pre_save(model_instance, add)
        if not value:
            value = self.get_prep_value('')
            setattr(model_instance, self.attname, value)
            if self.primary_key:
                setattr(model_instance, 'pk', value)
        return value


addrule([], ['^pgfields\.basic\.UUIDField'])
