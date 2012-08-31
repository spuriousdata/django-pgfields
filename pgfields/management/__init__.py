from django.db import connection, transaction, models
from django.db.models import signals
from django.db.utils import DatabaseError
from pgfields.viewtables import View, MatView

@transaction.autocommit
def create_views(sender, **kwargs):
    cursor = connection.cursor()
    for model in models.get_models(kwargs['app']):
        if issubclass(model, View):
            # Check if view exists
            sql = model.create_check()
            cursor.execute(*sql)
            result = cursor.fetchone()
            if not result[0]:
                # Create View
                sql = model.create_sql()
                cursor.execute(*sql)
            if issubclass(model, MatView):
                sql = MatView.storedproc_check()
                expected_resp = sql[2]
                sql = sql[:2]
                cursor.execute(*sql)
                res = cursor.fetchall()
                if res[0][0] != expected_resp:
                    for sql in MatView.storedproc_sql():
                        cursor.execute(sql, ())
                func = model.create_matview()
                try:
                    cursor.execute(*func)
                except DatabaseError as e:
                    if e.message.startswith('MatView') and e.message.find('already exists') != -1:
                        pass
                    else:
                        raise

signals.post_syncdb.connect(create_views)
