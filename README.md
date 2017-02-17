# "sentry" Debian Packaging

![BSD 3-clause licensed](http://img.shields.io/badge/license-BSD_3--clause-red.svg)
Latest release: [![sentry](http://img.shields.io/pypi/v/sentry.svg)](https://pypi.python.org/pypi/sentry/)

:loudspeaker: **This is in beta state and not production-ready yet!**

:mag_right: Building the package was tested on *Ubuntu Xenial* and *Debian Jessie*, runtime tests were done on *Jessie*.

:construction: For building on *Jessie*, you need [this patch](https://github.com/spotify/dh-virtualenv/pull/198) applied to ``dh-virtualenv``.

**Contents**

 * [What is this?](#what-is-this)
 * [How to build and install the package](#how-to-build-and-install-the-package)
 * [How to set up a simple "sentry" instance](#how-to-set-up-a-simple-sentry-instance)
 * [References](#references)
   * [Related Projects](#related-projects)
   * [Plugin Projects](#plugin-projects)


## What is this?

While the officially preferred way to install *Sentry* is via the project's Docker images by now,
there are still enough situations where you want to use a
[classic host-centric installation method](https://docs.sentry.io/server/installation/python/).
This project helps with that on Debian-like targets,
by providing DEB packaging for the server component.
This makes life-cycle management on production hosts a lot easier,
and avoids common drawbacks of ‘from source’ installs
like needing build tools and direct internet access in production environments.

The Debian packaging metadata in
[debian](https://github.com/1and1/debianized-sentry/tree/master/debian)
puts the `sentry` Python package and its dependencies as released on PyPI into a DEB package,
using [dh-virtualenv](https://github.com/spotify/dh-virtualenv).
The resulting *omnibus package* is thus easily installed to and removed from a machine,
but is not a ‘normal’ Debian `python-*` package. If you want that, look elsewhere.


## How to build and install the package

You need a build machine with all build dependencies installed, specifically
[dh-virtualenv](https://github.com/spotify/dh-virtualenv) in addition to the normal Debian packaging tools.
You can get it from [this PPA](https://launchpad.net/~spotify-jyrki/+archive/ubuntu/dh-virtualenv),
the [official Ubuntu repositories](http://packages.ubuntu.com/search?keywords=dh-virtualenv),
or [Debian packages](https://packages.debian.org/source/sid/dh-virtualenv).

This code requires and is tested with ``dh-virtualenv`` v1.0
– depending on your platform you might get an older version via the standard packages.
On *Jessie*, install it from ``jessie-backports``.
On *Xenial* you get *v0.11* by default, so you have to build *v1.0* from source.
See the [dh-virtualenv documentation](https://dh-virtualenv.readthedocs.io/en/latest/tutorial.html#step-1-install-dh-virtualenv) for that.

With tooling installed,
the following commands will install a *release* version of `sentry` into `/opt/virtualenvs/sentry/`,
and place a symlink for `sentry` into the machine's PATH.

```sh
git clone https://github.com/1and1/debianized-sentry.git
cd debianized-sentry/

sudo apt-get install build-essential debhelper devscripts equivs

# Extra steps on Jessie
echo "deb http://ftp.debian.org/debian jessie-backports main" \
    | sudo tee /etc/apt/sources.list.d/jessie-backports.list >/dev/null
sudo apt-get update -qq
sudo apt-get install -t jessie-backports cmake dh-virtualenv
# END jessie

# make sure pip is a recent version (e.g. Jessie still comes with 1.5.6)
if test $(pip --version | sed -re 's/[^0-9]*([0-9]+).*/\1/') -lt 8; then
    mkdir -p ~/bin ~/.local; pip install --user -U pip
    ln -s ~/.local/bin/pip ~/bin; exec $SHELL -l
fi
pip --version
# END pip update (should print 'pip 8.0.0 …' or higher)

sudo mk-build-deps --install debian/control
dpkg-buildpackage -uc -us -b
sudo dpkg -i ../sentry_*.deb
apt-cache show sentry
/usr/bin/sentry --version  # ensure it basically works
```

To list the installed version of `sentry` and all its dependencies, call this:

```sh
/opt/virtualenvs/sentry/bin/pip freeze | less
```


## How to set up a simple "sentry" instance

After installing the package, follow the steps in
[Installation with Python](https://docs.sentry.io/server/installation/python/#initializing-the-configuration),
taking into account the differences as outlined below.

For a simple experimental installation on a single host, install these additional packages:

```sh
sudo apt-get install redis-server postgresql
```

In the configuration, you need to at least generate a unique secret key, like this:

```sh
new_key=$(sentry config generate-secret-key | sed -e 's/[\/&]/\\&/g')
sed -i -re "s/^system.secret-key:.+\$/system.secret-key: '$new_key'/" /etc/sentry/config.yml
unset new_key
```

Alternatively, you can generate a whole new configuration set by calling ``sentry init /etc/sentry``.

To set up the *PostgreSQL* database, execute these commands in a ``root`` shell:

```sh
# Create DB user & schema
cd /tmp
sudo -u postgres -- createuser sentry --pwprompt
sudo -u postgres -- createdb -E utf-8 sentry
echo "GRANT ALL PRIVILEGES ON DATABASE sentry TO sentry;" \
    | sudo -u postgres -- psql -d template1

# Now change "PASSWORD" to the one you entered when creating the 'sentry' DB user!
${EDITOR:-vi} /etc/sentry/sentry.conf.py

# Create tables
sudo -u sentry SENTRY_CONF=/etc/sentry sentry upgrade
# After a while, you'll be prompted to create an initial Sentry user, say 'Y'es…
#   Would you like to create a user account now? [Y/n]:
```

Regarding services, you can ignore the *“Starting …”* as well as the *“Running Sentry as a Service”* sections.
The package already contains the necessary ``systemd`` units, and starting all services is done via ``systemctl``:

```sh
sudo systemctl enable sentry-web
sudo systemctl start sentry-web

# This should show 3 services in state "active (running)"
systemctl status 'sentry-*'
```

The web interface should now be reachable on port 9000
– consider putting a reverse proxy before the *uWSGI* server,
as mentioned in the *Sentry* documentation.

All *Sentry* services run as ``sentry.daemon``.
Note that the ``sentry`` user is not removed when purging the package,
but the ``/var/{log,opt}/sentry`` directories are.


## References

### Related Projects

 * [getsentry](https://github.com/getsentry) – The Sentry GitHub organization.
 * [onjin/docker-sentry-with-plugins](https://github.com/onjin/docker-sentry-with-plugins) – A Docker image with some pre-installed plugins, and related docs.
 * [clarkdave/logstash-sentry.rb](https://gist.github.com/clarkdave/edaab9be9eaa9bf1ee5f) – A Logstash output plugin to feed Sentry.
 * [Sentry for JIRA](https://marketplace.atlassian.com/plugins/sentry.io.jira_ac/cloud/overview) (Cloud only)


### Plugin Projects

| Project | Version | Description |
|:---:|:---:|:---:|
| [getsentry/sentry-plugins](https://github.com/getsentry/sentry-plugins#sentry-plugins) | [![sentry-plugins](http://img.shields.io/pypi/v/sentry-plugins.svg)](https://pypi.python.org/pypi/sentry-plugins/) | Official plugins by Sentry, includes GitHub and HipChat ones. |
| [Banno/getsentry-ldap-auth](https://github.com/Banno/getsentry-ldap-auth) | [![sentry-ldap-auth](http://img.shields.io/pypi/v/sentry-ldap-auth.svg)](https://pypi.python.org/pypi/sentry-ldap-auth/) | Use LDAP as an authentication source. |
| [Banno/getsentry-kafka](https://github.com/Banno/getsentry-kafka) | [![sentry-kafka](http://img.shields.io/pypi/v/sentry-kafka.svg)](https://pypi.python.org/pypi/sentry-kafka/) | Push events into Kafka topics. |
| [yoshiori/sentry-notify-github-issues](https://github.com/yoshiori/sentry-notify-github-issues) | [![sentry-notify-github-issues](http://img.shields.io/pypi/v/sentry-notify-github-issues.svg)](https://pypi.python.org/pypi/sentry-notify-github-issues/) | A notification plugin for GitHub issues. |
