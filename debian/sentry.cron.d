# Sentry data house-keeping

# m h   dom mon dow   user        command
7 0     *   *   *     sentry      . /etc/default/sentry && /usr/bin/sentry --config="$SENTRY_CONF" cleanup --days="$SENTRY_CLEANUP_DAYS"
