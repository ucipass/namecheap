#!/bin/sh

# Change into script directory
cd "${0%/*}"

# Load environment variables from .env
# Use --test-cert for testing
# export $(xargs <.env)
# export $(grep -v '^#' .env | xargs -d '\n')

echo $CERT_SAN

if [ -n $CERT_SAN ]; then

    certbot -d $CERT_FQDN,$CERT_SAN  \
    --text --non-interactive --agree-tos --email $CERT_EMAIL \
    --config-dir $CERT_DIR \
    --work-dir   $CERT_DIR \
    --logs-dir   $CERT_DIR \
    --manual-public-ip-logging-ok \
    --manual-auth-hook    "./namecheap.py --add" \
    --manual-cleanup-hook "./namecheap.py --delete"  \
    --manual --preferred-challenges dns \
    --force-renewal \
    certonly

else
    certbot -d $CERT_FQDN \
    --text --non-interactive --agree-tos --email $CERT_EMAIL \
    --config-dir $CERT_DIR \
    --work-dir   $CERT_DIR \
    --logs-dir   $CERT_DIR \
    --manual-public-ip-logging-ok \
    --manual-auth-hook    "./namecheap.py --add" \
    --manual-cleanup-hook "./namecheap.py --delete"  \
    --manual --preferred-challenges dns \
    --force-renewal \
    certonly

fi


# ./namecheap.py --add

