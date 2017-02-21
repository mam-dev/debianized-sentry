# Sentry data house-keeping

SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
MAILTO=root@localhost

# m h   dom mon dow   user        command
7 0     *   *   *     sentry      . /etc/default/sentry && /usr/bin/sentry >/var/log/sentry/cleanup.log 2>&1 --config="$SENTRY_CONF" cleanup --days="$SENTRY_CLEANUP_DAYS"
