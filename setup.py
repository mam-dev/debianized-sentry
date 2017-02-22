#! /usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=
""" Debian packaging for Sentry, a modern realtime error logging and aggregation platform.

    | Copyright ©  2017 1&1 Group
    | BSD 3-clause license, see LICENSE for details.

    This puts the ``sentry`` Python package and its dependencies as released
    on PyPI into a DEB package, using ``dh-virtualenv``.
    The resulting *omnibus package* is thus easily installed to and removed
    from a machine, but is not a ‘normal’ Debian ``python-*`` package.

    The final package includes the official ``sentry-plugins`` and some other
    commonly needed plugins.

    See the `GitHub README`_ for more.

    .. _`GitHub README`: https://github.com/1and1/debianized-sentry#sentry-debian-packaging
"""
import os
import re
import sys
import json
import rfc822
import textwrap
import subprocess

try:
    from setuptools import setup
except ImportError as exc:
    raise RuntimeError("setuptools is missing ({1})".format(exc))


# get external project data
pkg_version = subprocess.check_output("parsechangelog | grep ^Version:", shell=True)
upstream_version, maintainer_version = pkg_version.split()[1].rsplit('~', 1)[0].split('-', 1)
maintainer_version = maintainer_version.replace('~rc', 'rc').replace('~dev', '.dev')
pypi_version = upstream_version + '.' + maintainer_version

with open('debian/control') as control_file:
    deb_source = rfc822.Message(control_file)
    deb_binary = rfc822.Message(control_file)

maintainer, email = re.match(r'(.+) <([^>]+)>', deb_source['Maintainer']).groups()
desc, long_desc = deb_binary['Description'].split('.', 1)
desc, pypi_desc = __doc__.split('\n', 1)
long_desc = textwrap.dedent(pypi_desc) + textwrap.dedent(long_desc).replace('\n.\n', '\n\n')


# build setuptools metadata
project = dict(
    name='debianized-' + deb_source['Source'],
    version=pypi_version,
    author=maintainer,
    author_email=email,
    license='BSD 3-clause',
    description=desc.strip(),
    long_description=textwrap.dedent(long_desc).strip(),
    url=deb_source['Homepage'],
    classifiers=[
        # Details at http://pypi.python.org/pypi?:action=list_classifiers
        'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Logging',
    ],
    keywords='debian-packages dh-virtualenv sentry deployment devops omnibus-packages'.split(),
    install_requires=[
        # core
        'sentry[postgres]==' + upstream_version,
        'sentry-plugins==' + upstream_version,

        # 3rd party
        'sentry-ldap-auth==2.3',
        'sentry-kafka==1.1',
    ],
    packages=[],
)


# 'main'
__all__ = ['project']
if __name__ == '__main__':
    if '--metadata' in sys.argv[:2]:
        json.dump(project, sys.stdout, default=repr, indent=4, sort_keys=True)
        sys.stdout.write('\n')
    elif '--tag' in sys.argv[:2]:
        subprocess.call("git tag -a 'v{version}' -m 'Release v{version}'"
                        .format(version=pypi_version), shell=True)
    else:
        setup(**project)
