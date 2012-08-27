try:
    from south.modelsinspector import add_introspection_rules as addrule
except ImportError:
    def addrule(*args, **kwargs):
        pass

from django.db.backends.signals import connection_created
__initializers = []
def register_initializer(func):
    __initializers.append(func)

def run_initializers(sender, **kwargs):
    for func in __initializers:
        try:
            func(sender, **kwargs)
        except:
            pass
connection_created.connect(run_initializers)
