# "sentry" Debian Packaging

![BSD 3-clause licensed](http://img.shields.io/badge/license-BSD_3--clause-red.svg)
Latest release: [![sentry](http://img.shields.io/pypi/v/sentry.svg)](https://pypi.python.org/pypi/sentry/)

:loudspeaker: **This is in alpha state and not production-ready yet!**

:construction: For building on *Jessie*, you need [this patch](https://github.com/spotify/dh-virtualenv/pull/198) applied to ``dh-virtualenv``.


## What is this?

While the officially preferred way to install *Sentry* is via the project's Docker images by now,
there are still enough situations where you prefer a
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
The resulting package is thus easily installed to and removed from a machine,
but is not a ‘normal’ Debian `python-*` package. If you want that, look elsewhere.


## How to build and install the package?

You need of course a machine with the build dependencies installed, specifically
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
sudo apt-get install -t jessie-backports cmake dh-virtualenv

# make sure pip is a recent version (e.g. Jessie still comes with 1.5.6)
# you may omit this in newer systems, or appropriately configured accounts
mkdir -p ~/bin ~/.local
pip install --user -U pip
ln -s ~/.local/bin/pip ~/bin

sudo mk-build-deps --install debian/control
dpkg-buildpackage -uc -us -b
sudo dpkg -i ../sentry_*.deb
apt-cache show sentry
/usr/bin/sentry --version  # ensure it basically works
```

The version of `sentry` and other core components used is specified in `debian/rules`.


## How to configure a simple "sentry" instance?

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
