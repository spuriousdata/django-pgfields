from distutils.core import setup

setup(
    name='django-pgfields',
    version='0.0.2',
    author="Mike O'Malley",
    author_email='mikeo@outriggermedia.com',
    description='Postgres-specific db fields for django',
    long_description=open('README.rst').read(),
    license='LICENSE',
    url='http://github.com/spuriousdata/django-pgfields',
    packages=['pgfields', 'pgfields.hstore', 'pgfields.management'],
    include_package_data=True,
    install_requires=[
        'Django >= 1.4.0',
        'psycopg2',
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Environment :: Web Environment",
        #"License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
    ],
)
