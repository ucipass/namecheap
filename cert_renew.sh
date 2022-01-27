#!/bin/sh

# Change into script directory
cd "${0%/*}"


# Load environment variables from .env
# Use --test-cert for testing

# export $(grep -v '^#' .env | xargs -d '\n')

# ./namecheap.py --add

certbot -d $CERT_FQDN \
--text --non-interactive --agree-tos --email $CERT_EMAIL \
--config-dir $CERT_DIR \
--work-dir   $CERT_DIR \
--logs-dir   $CERT_DIR \
--manual-public-ip-logging-ok \
--manual-auth-hook    "./namecheap.py --add" \
--manual-cleanup-hook "./namecheap.py --delete"  \
--manual --preferred-challenges dns \
--test-cert \
certonly
