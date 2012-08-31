from django.db import connection, transaction
from django.db.models import signals
from pgfields.views import View, MatView

@transaction.autocommit
def create_views(sender, **kwargs):
    cursor = connection.cursor()
    for model in models.get_models(kwargs['app']):
        if issubclass(model, View):
            if issubclass(model, MatView):
                sql = MatView.storedproc_check()
                expected_rows = sql[2]
                sql = sql[:2]
                cursor.execute(*sql)
                if len(cursor.fetchall()) != expected_rows:
                    for sql in MatView.storedproc_sql():
                        if type(sql) != tuple:
                            sql = (sql,)
                        cursor.execute(*sql)
            # Create View
            sql = model.create_sql()
            cursor.execute(*sql)
            # Create MatView
            if issubclass(model, MatView):

signals.post_syncdb.connect(create_views)
