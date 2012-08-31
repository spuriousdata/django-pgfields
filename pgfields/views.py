from psycopg2.extensions import adapt
from django.db import models
from django.core.exceptions import ImproperlyConfigured


class View(object):
    class Meta:
        managed = False

    @classmethod
    def viewname(cls):
        if hasattr(cls, 'viewname'):
            return cls.viewname
        module = cls.__module__.lower().replace('models.', '').replace('.','')
        view = cls.__name__.lower()
        return "%s_%s" % (module, view)

    @classmethod
    def create_sql(cls):
        if not hasattr(cls, 'sql'):
            raise ImproperlyConfigured, "View classes require View.sql to be defined"

        return ("CREATE VIEW %s AS %s", (View.viewname(), cls.sql))

    @staticmethod
    def create_check():
        return ("SELECT EXISTS(SELECT %s FROM pg_??", "")

class MatView(View):
    # Idea and sql from http://tech.jonathangardner.net/wiki/PostgreSQL/Materialized_Views
    @staticmethod
    def storedproc_sql():
        sql = []
        sql.append("""
        CREATE TABLE IF NOT EXISTS pgfields_matviews (
            matview_name NAME NOT NULL PRIMARY KEY,
            view_name NAME NOT NULL,
            last_refresh TIMESTAMP WITH TIME ZONE
        );
        """)
        sql.append("""
        CREATE OR REPLACE FUNCTION pgfields_create_matview(NAME, NAME)
        RETURNS VOID
        LANGUAGE plpgsql AS '
        DECLARE
            matview ALIAS FOR $1;
            view_name ALIAS FOR $2;
            entry pgfields_matviews%ROWTYPE;
        BEGIN
            SELECT * INTO entry FROM pgfields_matviews WHERE mv_name = matview;

            IF FOUND THEN
                RAISE EXCEPTION ''MatView %% already exists.'', matview;
            END IF;

            /*
            EXECUTE ''REVOKE ALL ON '' || view_name || '' FROM PUBLIC'';

            EXECUTE ''GRANT SELECT ON '' || view_name || '' TO PUBLIC'';
            */

            EXECUTE ''CREATE TABLE '' || matview || '' AS SELECT * FROM '' || view_name;

            /*
            EXECUTE ''REVOKE ALL ON '' || matview || '' FROM PUBLIC'';

            EXECUTE ''GRANT SELECT ON '' || matview || '' TO PUBLIC'';
            */

            INSERT INTO pgfields_matviews (matview_name, view_name, last_refresh)
                VALUES (matview, view_name, CURRENT_TIMESTAMP);

            RETURN;
        END
        ';
        """)
        sql.append("""
        CREATE OR REPLACE FUNCTION pgfields_drop_matview(NAME)
        RETURNS VOID
        LANGUAGE plpgsql AS '
        DECLARE
            matview ALIAS FOR $1
            entry pgfields_matviews%ROWTYPE;
        BEGIN
            SELECT * INTO entry FROM pgfields_matviews WHERE matview_name = matview;
            IF NOT FOUND THEN
                RAISE EXCEPTION ''MatView %% does not exist.'', matview;
            END IF;

            EXECUTE ''DROP TABLE '' || matview;
            DELETE FROM pgfields_matviews WHERE matview_name = matview;

            RETURN;
        END
        ';
        """)
        sql.append("""
        CREATE OR REPLACE FUNCTION pgfields_refresh_matview(NAME)
        RETURNS VOID
        LANGUAGE plpgsql AS '
        DECLARE
            matview ALIAS FOR $1
            entry pgfields_matviews%ROWTYPE;
        BEGIN
            SELECT * INTO entry FROM pgfields_matviews WHERE matview_name = matview;

            IF NOT FOUND THEN
                RAISE EXCEPTION MatView %% does not exist.'', matview;
            END IF;

            EXECUTE ''DELETE FROM '' || matview;
            EXECUTE ''INSERT INTO '' || matview || '' SELECT * FROM '' || entry.view_name;

            UPDATE pgfields_matviews SET last_refresh=CURRENT_TIMESTAMP
                WHERE matview_name=matview;

            RETURN;
        END
        ';
        """)

        return sql

    @staticmethod
    def storedproc_check():
        return ("SELECT COUNT(*) FROM pg_proc WHERE proname IN (%s, %s, %s)", (
            'pgfields_create_matview',
            'pgfields_drop_matview',
            'pgfields_refresh_matview',
        ), 3)

    @classmethod
    def create_matview(cls):
        if not hasattr(cls, 'name') or not hasattr(cls, 'view'):
            raise ImproperlyConfigured, "MatView classes require MatView.name and MatView.view to be defined"
        return ("SELECT pgfields_create_matview(%s, %s)", MatView.name, MatView.view)

