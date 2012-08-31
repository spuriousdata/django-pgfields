===============
django-pgfields
===============

Implementation of various postgres-specfic pieces of functionality for django.
Current features include: array types, hstore types, a uuid field, an enum
field, a view model mixin, and a materialized view model mixin.

django-pgfields will take care of all pre-use database operations, such as
'CREATE TYPE' for the ENUMField, 'CREATE VIEW' for the View mixin, and creation
of the view and storage table for the materialized view mixin.

-----
Usage
-----

###########
Field Types
###########
For all field types, simply:
    import pgfields

    class Student(models.Model):
        id = pgfields.UUIDField()
        name = models.CharField(max_length=256)
        grades = pgfields.CharArray()
        grade_number_mapping = pgfields.DictionaryField()

###########
View Types
###########
In order to utilize the View and MatView model mixins, you'll have to add
'pgfields' to INSTALLED_APPS. Then you can define your view this way:

    import pgfields

    class MyView(models.Model, pgfields.View):
        sql = "SELECT list,of,stuff FROM tablename ORDER BY date"

This will create a postgres view called <modelname>_myview. Running syncdb (or
migrate, if you're using South to manage this model) will take care of the creation of the view
utilizing the query provided in the `sql` variable.

------------
Requirements
------------

psycopg2

This module has only been tested against django 1.4.1
