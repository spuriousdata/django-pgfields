from arrays import *
from pgfields.hstore import *
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(rules=[], patterns=['pgfields\.hstore\.hstore'])
    add_introspection_rules(rules=[], patterns=['pgfields\.arrays'])
except ImportError:
    pass
