Riddler README
==============

Riddler is a web application that can help recruiters to do job interview
technical tests. Riddler provides an administration zone to enter questions and
create tests, and a test zone for applicants.

Features
--------

* NOT a multiple choice, the candidate have to type the answer
* Once opened, a question must be answered, the candidate can't open multiple
  questions at a time and can't answer in the order he wants
* Each answer is timed, so you can see if the applicant has stuck on a question
* A test can be time limited

Setup
-----

Riddler is packaged for the Debian Wheezy distro, but since its a standard
Django application, it should be easy to install it on any other distro.

Install packages
~~~~~~~~~~~~~~~~

Add this lines in your ``/etc/apt/source.list`` file::

    deb http://debian.tecknet.org/debian wheezy tecknet
    deb-src http://debian.tecknet.org/debian wheezy tecknet

Add the Tecknet repositories key in your keyring:

    # wget http://debian.tecknet.org/debian/public.key -O - | apt-key add -

Then, update and install::

    # aptitude update
    # aptitude install riddler

The installation procedure will configure the database (SQLite by default) and
collect all static files in the ``/var/lib/riddler/`` directory.

Configure Gunicorn
~~~~~~~~~~~~~~~~~~

The next step is to configure gunicorn to serve the riddler application: in the
``/etc/gunicorn.d/`` directory, copy the ``riddler.example`` file
to ``riddler``::

    # cd /etc/gunicorn.d
    # cp riddler.example riddler

You can customize the file to add or change gunicorn options such as the
listening port (by default 9001) or the number of workers to start.

Restart gunicorn to start Riddler::

    # service gunicorn restart

Configure the web server
~~~~~~~~~~~~~~~~~~~~~~~~

The last thing to do is to configure a web server to reverse proxy the Riddler
application served by Gunicorn, and to serve static files. Here is an example
for nginx::

    # cat /etc/nginx/site-enabled/riddler
    server {
        location / {
            proxy_pass_header Server;
            proxy_set_header Host $http_host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_pass http://127.0.0.1:9001/;
            proxy_redirect default;
        }

        location /static {
            alias /var/lib/riddler/static;
        }

        location /media {
            alias /var/lib/riddler/media;
        }
    }

Use it
~~~~~~

Create an admin user using ``riddleradm``::

    # riddleradm createsuperuser
    Username (leave blank to use 'stallman'): stallman
    E-mail address: rms@example.org
    Password: emacs
    Password (again): emacs
    Superuser created successfully.

Access to your riddler admin using ``http://riddler-srv/admin/``.


Todo / Changelog
-----------------

See the TODO.rst and CHANGELOG.rst files

Contribute
----------

You can send your pull-request for Riddler through Github:

    https://github.com/NaPs/Riddler

I also accept well formatted git patches sent by email.

Feel free to contact me for any question/suggestion/patch: <antoine@inaps.org>.