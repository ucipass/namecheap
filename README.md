# Namecheap Dynamic Update Script
This program has two use cases:
- Update namecheap DNS records using a YAML file
- Use it with letsencrypt certbot -manual-auth-hook and --manual-clean-up script to authenticate certificates.

# Environment variables
- NAMECHEAP_USER=[USER]
- NAMECHEAP_APIKEY=[APIKEY]
- NAMECHEAP_SUBDOMAIN=[sub-domain e.g. example]
- NAMECHEAP_TOPDOMAIN=[top level domain e.g com]
- CERT_FQDN=[Fully qualified domain name of the certificate]
- CERT_SAN=[Subject Alternative Name, optinal]
- CERT_EMAIL=[Email for certificate registration]
- CERT_DIR=[certbot certificate directory]

# Certbot update example (use --test-cert for testing)
certbot -d \$CERT_FQDN,\$CERT_SAN \
--text --non-interactive --agree-tos --email \$CERT_EMAIL \
--config-dir \$CERT_DIR \
--work-dir   \$CERT_DIR \
--logs-dir   \$CERT_DIR  \
--manual-public-ip-logging-ok \
--manual-auth-hook    "./namecheap.py --add" \
--manual-cleanup-hook "./namecheap.py --delete"  \
--manual --preferred-challenges dns \
certonly

