# "sentry" Debian Packaging

![BSD 3-clause licensed](http://img.shields.io/badge/license-BSD_3--clause-red.svg)
Latest release: [![sentry](http://img.shields.io/pypi/v/sentry.svg)](https://pypi.python.org/pypi/sentry/)

:loudspeaker: **This is in alpha state and not production-ready yet!**


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

This code is tested using ``dh-virtualenv`` v1.0, depending on your platform you might get older versions.
On *Xenial* you get *v0.11* by default, which has a chance to work, but you possibly have to build *v1.0* from source.
See the [dh-virtualenv documentation](https://dh-virtualenv.readthedocs.io/en/latest/tutorial.html#step-1-install-dh-virtualenv) for that.

With tooling installed,
the following commands will install a *release* version of `sentry` into `/opt/virtualenvs/sentry/`,
and place a symlink for `sentry` into the machine's PATH.

```sh
git clone https://github.com/1and1/debianized-sentry.git
cd debianized-sentry/

sudo apt-get install build-essential debhelper devscripts equivs
sudo mk-build-deps --install debian/control

dpkg-buildpackage -uc -us -b
sudo dpkg -i ../sentry_*.deb
apt-cache show sentry
/usr/bin/sentry --version  # ensure it basically works
```

The version of `sentry` and other core components used is specified in `debian/rules`.


## How to configure a simple "sentry" instance?

To get a running `sentry-server` instance, you need to install the package and then add the necessary configuration.
This can be done automatically using the [sentry-puppet](https://github.com/1and1/sentry-puppet) module (see there for details), which also gives you instant theming and NginX proxying to an external port.
Otherwise, use the following instructions to do so
– but be aware that these are only appropriate for workstation installations of a single developer.

So once the package is installed as shown in the previous section,
use these commands as `root` to configure and start your `sentry` server:

```sh
apt-get install supervisor
addgroup sentry
adduser sentry --ingroup sentry --home /var/lib/sentry --system --disabled-password
( export LOGNAME=sentry && cd /tmp && /usr/sbin/sentry-server --gen-config )
cp /tmp/gen-config/supervisor-sentry.conf /etc/supervisor/conf.d/sentry-server.conf
echo >>/etc/supervisor/conf.d/sentry-server.conf "directory = /var/lib/sentry"
service supervisor start
supervisorctl update
supervisorctl tail -f sentry-server
```

Then, in a 2nd non-root shell:

```sh
sentry use "http://localhost:3141/"
sentry login root --password=
  sentry user -m root password=…
sentry user -c local # … and enter password
sentry login local # … and enter password
sentry index -c dev
sentry index dev bases=root/pypi
sentry use dev --set-cfg # be aware this changes 'index_url' of several configs in your $HOME
```

Finally, you can open the [web interface](http://localhost:3141/) and browse your shiny new local repositories.
For further details, consult sentry's
[Release Process Quickstart](http://doc.sentry.net/latest/quickstart-releaseprocess.html)
documentation, starting with *“sentry install: installing a package.”*
