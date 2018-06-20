# "sentry.io" Debian Packaging

![BSD 3-clause licensed](https://img.shields.io/badge/license-BSD_3--clause-red.svg)
[![debianized-sentry](https://img.shields.io/pypi/v/debianized-sentry.svg)](https://pypi.python.org/pypi/debianized-sentry/)
[![sentry](https://img.shields.io/pypi/v/sentry.svg)](https://pypi.python.org/pypi/sentry/)

:mag_right: Building the package was tested on *Ubuntu Xenial* and *Debian Jessie*, runtime tests were done on *Jessie*.

**Contents**

 * [What is this?](#what-is-this)
 * [How to build and install the package](#how-to-build-and-install-the-package)
 * [Trouble-Shooting](#trouble-shooting)
   * ['pkg-resources not found' or similar during virtualenv creation](#pkg-resources-not-found-or-similar-during-virtualenv-creation)
 * [How to set up a simple "sentry" instance](#how-to-set-up-a-simple-sentry-instance)
   * [Basic Configuration](#basic-configuration)
   * [Database Setup](#database-setup)
   * [Starting Services](#starting-services)
   * [Upgrades and Auto-Migration](#upgrades-and-auto-migration)
   * [Changing the Service Unit Configuration](#changing-the-service-unit-configuration)
 * [Configuration Files](#configuration-files)
 * [Data Directories](#data-directories)
 * [Release Notes](#release-notes)
   * [Release 9.0.0 (rc1)](#release-900-rc1)
 * [References](#references)
   * [Related Projects](#related-projects)
   * [Plugin Projects](#plugin-projects)


## What is this?

While the [officially preferred way](https://github.com/getsentry/onpremise)
to install *Sentry* is via the project's Docker images by now,
there are still enough situations where you want to use a
[classic host-centric installation method](https://docs.sentry.io/server/installation/python/).
This project helps with that on Debian-like targets,
by providing DEB packaging for the server component.
This makes life-cycle management on production hosts a lot easier, and
[avoids common drawbacks](https://nylas.com/blog/packaging-deploying-python/) of ‘from source’ installs,
like needing build tools and direct internet access in production environments.

> **A typical on-premise deployment with application data pushed from the Internet**
> ![Sentry.io On-Premise Deployment Overview](https://raw.githubusercontent.com/1and1/debianized-sentry/master/docs/_static/img/sentry-deploy-800px.png)

The Debian packaging metadata in
[debian](https://github.com/1and1/debianized-sentry/tree/master/debian)
puts the `sentry` Python package and its dependencies as released on PyPI into a DEB package,
using [dh-virtualenv](https://github.com/spotify/dh-virtualenv).
The resulting *omnibus package* is thus easily installed to and removed from a machine,
but is not a ‘normal’ Debian `python-*` package. If you want that, look elsewhere.

The final package includes the official ``sentry-plugins``,
see ``install_requires`` in ``setup.py`` for others that are added by default.
This is also the place where you can put in your own
– only use versioned dependencies so package builds are reproducible.


## How to build and install the package

You need a build machine with all build dependencies installed, specifically
[dh-virtualenv](https://github.com/spotify/dh-virtualenv) in addition to the normal Debian packaging tools.
You can get it from [this PPA](https://launchpad.net/~spotify-jyrki/+archive/ubuntu/dh-virtualenv),
the [official Ubuntu repositories](http://packages.ubuntu.com/search?keywords=dh-virtualenv),
or [Debian packages](https://packages.debian.org/source/sid/dh-virtualenv).

This code requires and is tested with ``dh-virtualenv`` v1.0
– depending on your platform you might get an older version via the standard packages.
On *Jessie*, install it from ``jessie-backports``.
*Zesty* provides a package for Ubuntu that works on older releases too,
see *“Extra steps on Ubuntu”* below for how to use it.
In all other cases build *v1.0* from source,
see the [dh-virtualenv documentation](https://dh-virtualenv.readthedocs.io/en/latest/tutorial.html#step-1-install-dh-virtualenv) for that.

With tooling installed,
the following commands will install a *release* version of `sentry` into `/opt/venvs/sentry/`,
and place a symlink for `sentry` into the machine's PATH.

```sh
git clone https://github.com/1and1/debianized-sentry.git
cd debianized-sentry/
# or "pip download --no-deps --no-binary :all: debianized-sentry" and unpack the archive

sudo apt-get install build-essential debhelper devscripts equivs

# Extra steps on Jessie
echo "deb http://ftp.debian.org/debian jessie-backports main" \
    | sudo tee /etc/apt/sources.list.d/jessie-backports.list >/dev/null
sudo apt-get update -qq
sudo apt-get install -t jessie-backports cmake dh-virtualenv
# END jessie

# Extra steps on Ubuntu
( cd /tmp && curl -LO "http://mirrors.kernel.org/ubuntu/pool/universe/d/dh-virtualenv/dh-virtualenv_1.0-1_all.deb" )
sudo dpkg -i /tmp/dh-virtualenv_1.0-1_all.deb
# END Ubuntu

sudo mk-build-deps --install debian/control
dpkg-buildpackage -uc -us -b
dpkg-deb -I ../sentry.io_*.deb
```

The resulting package, if all went well, can be found in the parent of your project directory.
You can upload it to a Debian package repository via e.g. `dput`, see
[here](https://github.com/jhermann/artifactory-debian#package-uploading)
for a hassle-free solution that works with *Artifactory* and *Bintray*.

You can also install it directly on the build machine:

```sh
sudo dpkg -i ../sentry.io_*.deb
/usr/bin/sentry --version  # ensure it basically works
```

To list the installed version of `sentry` and all its dependencies, call this:

```sh
/opt/venvs/sentry/bin/pip freeze | less
```


## Trouble-Shooting

### 'pkg-resources not found' or similar during virtualenv creation

If you get errors regarding ``pkg-resources`` during the virtualenv creation,
update your build machine's ``pip`` and ``virtualenv``.
The versions on many distros are just too old to handle current infrastructure (especially PyPI).

This is the one exception to “never sudo pip”, so go ahead and do this:

```sh
sudo pip install -U pip virtualenv
```

Then try building the package again.


## How to set up a simple "sentry" instance

After installing the package, follow the steps in
[Installation with Python](https://docs.sentry.io/server/installation/python/#initializing-the-configuration),
taking into account the differences as outlined below.


### Basic Configuration

In case you want to test the setup procedure in a Docker container,
start one using ``docker run --rm -it -v $PWD/..:/data debian:8 bash``
and then execute these commands:

```sh
PKG=$(ls -rt1 /data/sentry.io_*~jessie_amd64.deb | tail -n1)
apt-get update
apt-get install sudo $(dpkg -I $PKG | egrep Depends: | cut -f2- -d: | sed -re 's/\([^)]+\),?|,//g')
dpkg -i $PKG
```

Note that this assumes you built the ``sentry.io`` binary package before that,
and called ``docker`` from the workdir of this project (otherwise adapt the volume mapping).

For a simple experimental installation on a single host or in Docker,
also install these additional packages for related services:

```sh
sudo apt-get install redis-server postgresql postgresql-contrib
```

In the configuration, you need to at least generate a unique secret key, like this:

```sh
new_key=$(sentry config generate-secret-key | sed -e 's/[\/&]/\\&/g')
sed -i -re "s/^system.secret-key:.+\$/system.secret-key: '$new_key'/" /etc/sentry/config.yml
unset new_key
```

If you use a fresh configuration set as produced by ``sentry init /etc/sentry``,
e.g. in your configuration management,
be sure to diff against the files in ``etc`` to make sure you don't lose
changes like the correct filestore location.


### Database Setup

To set up the *PostgreSQL* database, execute these commands in a ``root`` shell:

```sh
# Create DB user & schema
cd /tmp
sudo -u postgres -- createuser sentry --pwprompt
sudo -u postgres -- createdb -E utf-8 sentry
echo "GRANT ALL PRIVILEGES ON DATABASE sentry TO sentry;" \
    | sudo -u postgres -- psql -d template1
echo "ALTER ROLE sentry superuser;" \
    | sudo -u postgres -- psql -d template1

# Now change "PASSWORD" to the one you entered when creating the 'sentry' DB user!
${EDITOR:-vi} /etc/sentry/sentry.conf.py

# Create tables
sudo -u sentry SENTRY_CONF=/etc/sentry sentry upgrade
# After a while, you'll be prompted to create an initial Sentry user, say 'Y'es…
#   Would you like to create a user account now? [Y/n]:
#
# Make this user a super user (admin), there is a prompt for that too.

# Revoke temp. superuser privileges
echo "ALTER ROLE sentry nosuperuser;" \
    | sudo -u postgres -- psql -d template1
```
See getsentry/sentry#6098 for details regarding the temporary superuser privileges.


### Starting Services

Regarding services, you can ignore the *“Starting …”* as well as the *“Running Sentry as a Service”* sections
of Sentry.io's ‘on premise’ instructions.
The package already contains the necessary ``systemd`` units, and starting all services is done via ``systemctl``:

```sh
# sentry-web requires sentry-worker and sentry-cron,
# so there is no need to start / enable them separately
sudo systemctl enable sentry-web
sudo systemctl start sentry-web

# This should show 3 services in state "active (running)"
systemctl status 'sentry-*' | grep -B2 Active:
```

The web interface should now be reachable on port 9000
– consider putting a reverse proxy before the *uWSGI* server,
as mentioned in the *Sentry* documentation.

All *Sentry* services run as ``sentry.daemon``.
Note that the ``sentry`` user is not removed when purging the package,
but the ``/var/{log,opt}/sentry`` directories and the configuration files are.


### Upgrades and Auto-Migration

After an upgrade, the services do **not** restart automatically by default,
to give you a chance to run the DB migration manually,
and then restart them yourself.
That means you should pin the version of the ``sentry`` package,
be it on the production hosts or in your configuration management
(i.e. do *not* use ``latest``).

If on the other hand you set ``SENTRY_AUTO_MIGRATE=true`` in ``/etc/default/sentry``,
then during package configuration the migration is performed.
If it is successful, the services are started again.
Details of the migration are logged to ``/var/log/sentry/upgrade-‹version›-‹timestamp›.log``.
To re-try a failed migration, use ``dpkg-reconfigure sentry.io``.


### Changing the Service Unit Configuration

The best way to change or augment the configuration of a *systemd* service
is to use a ‘Drop-In’ file.
For example, to increase the limit for open file handles
above the system defaults, use this in a **``root``** shell:

```sh
unit=sentry-web

# Change max. number of open files for ‘$unit’…
mkdir -p /etc/systemd/system/$unit.service.d
cat >/etc/systemd/system/$unit.service.d/limits.conf <<'EOF'
[Service]
LimitNOFILE=8192
EOF

systemctl daemon-reload
systemctl restart $unit

# Check that the changes are effective…
systemctl cat $unit
let $(systemctl show $unit -p MainPID)
cat "/proc/$MainPID/limits" | egrep 'Limit|files'
```


## Configuration Files

 * ``/etc/default/sentry`` – Operational parameters like data retention and global log levels.
 * ``/etc/sentry/config.yml`` – The Sentry YAML configuration (email, Redis, storage).
 * ``/etc/sentry/sentry.conf.py`` – The Sentry dynamic configuration (database, and everything else).
 * ``/etc/cron.d/sentry`` – The house-keeping cron job that calls ``sentry cleanup`` each day.

 :information_source: Please note that the files in ``/etc/sentry`` are *not* world-readable, since they contain passwords.


## Data Directories

 * ``/var/log/sentry`` – Extra log files (by the cron job).
 * ``/var/opt/sentry`` – Data files, the ``files`` subdirectory contains the default blob storage (e.g. images).

You should stick to these locations, because the maintainer scripts have special handling for them.
If you need to relocate, consider using symbolic links to point to the physical location.


## Release Notes

### Release 9.0.0 (rc1)

General notes:

* The build was tested under *Xenial* so far (and only very cursory).
* ``psycopg2`` is installed from source, because the ``manylinux1`` wheel causes problems during ELF dynamic loading / linking.

If you're upgrading to version 9, make sure you are using the right database engine setting
in ``/etc/sentry.conf.py``:


```py
…
DATABASES = {
    'default': {
        'ENGINE': 'sentry.db.postgres',
…
```


## References

### Related Projects

 * [getsentry](https://github.com/getsentry) – The Sentry GitHub organization.
 * [onjin/docker-sentry-with-plugins](https://github.com/onjin/docker-sentry-with-plugins) – A Docker image with some pre-installed plugins, and related docs.
   * Based on [slafs/sentry-docker](https://github.com/slafs/sentry-docker)
 * [clarkdave/logstash-sentry.rb](https://gist.github.com/clarkdave/edaab9be9eaa9bf1ee5f) – A Logstash output plugin to feed Sentry.
 * [Sentry for JIRA](https://marketplace.atlassian.com/plugins/sentry.io.jira_ac/cloud/overview) (Cloud only)
 * [Springerle/debianized-pypi-mold](https://github.com/Springerle/debianized-pypi-mold) – Cookiecutter to create this type of project.
 * [c7n_sentry](https://github.com/capitalone/cloud-custodian/tree/master/tools/c7n_sentry) – Generic *Cloud Watch* log scanner /subscription that searches for tracebacks, extracts frames, and posts them to Sentry.


### Plugin Projects

| Project | Version | Description |
|:---|:---|:---|
| [getsentry/sentry-plugins](https://github.com/getsentry/sentry-plugins#sentry-plugins) | [![sentry-plugins](https://img.shields.io/pypi/v/sentry-plugins.svg)](https://pypi.python.org/pypi/sentry-plugins/) | Official plugins by Sentry, includes GitHub and HipChat ones. |
| [Banno/getsentry-ldap-auth](https://github.com/Banno/getsentry-ldap-auth) | [![sentry-ldap-auth](https://img.shields.io/pypi/v/sentry-ldap-auth.svg)](https://pypi.python.org/pypi/sentry-ldap-auth/) | Use LDAP as an authentication source. |
| [Banno/getsentry-kafka](https://github.com/Banno/getsentry-kafka) | [![sentry-kafka](https://img.shields.io/pypi/v/sentry-kafka.svg)](https://pypi.python.org/pypi/sentry-kafka/) | Push events into Kafka topics. |
| [simonpercivall/sentry-mailagain](https://github.com/simonpercivall/sentry-mailagain/) | [![](https://img.shields.io/pypi/v/sentry-mailagain.svg)](https://pypi.python.org/pypi/sentry-mailagain/) | Resend the mail notification on receiving new events in an unresolved group. |
| [andialbrecht/sentry-responsible](https://github.com/andialbrecht/sentry-responsible) | [![](https://img.shields.io/pypi/v/sentry-responsible.svg)](https://pypi.python.org/pypi/sentry-responsible/) | This extension adds a widget on the sidebar of a event page to mark team members as being responsible for a event. |
| [dmclain/sentry-export](https://github.com/dmclain/sentry-export) | [![](https://img.shields.io/pypi/v/sentry-export.svg)](https://pypi.python.org/pypi/sentry-export/) | Allow developers to export event data in self-service. |
| [yoshiori/sentry-notify-github-issues](https://github.com/yoshiori/sentry-notify-github-issues) | [![sentry-notify-github-issues](https://img.shields.io/pypi/v/sentry-notify-github-issues.svg)](https://pypi.python.org/pypi/sentry-notify-github-issues/) | A notification plugin for GitHub issues. |
| [gisce/sentry-irc](https://github.com/gisce/sentry-irc) | [![](https://img.shields.io/pypi/v/sentry-irc.svg)](https://pypi.python.org/pypi/sentry-irc/) | Send notifications to IRC channels. |
