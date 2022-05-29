# Namecheap Dynamic Update Script
This script works with the Namecheap DNS service for two use cases:
1. Retrieve, Update and Delete namecheap DNS records using a YAML file
2. Use it with letsencrypt certbot -manual-auth-hook and --manual-clean-up script to authenticate for certificate renewal.

# Environment variables
- NAMECHEAP_USER=[USER]
- NAMECHEAP_APIKEY=[APIKEY]
- NAMECHEAP_SUBDOMAIN=[sub-domain e.g. example]
- NAMECHEAP_TOPDOMAIN=[top level domain e.g com]

# Letsencrypt Certbot validation
When the python script is invoked with certbot's -manual-auth-hook and --manual-clean-up options, certbot sets 2 environment variables (CERTBOT_DOMAIN, CERTBOT_VALIDATION) that are used by this script to update a TXT records in the zone for DNS validation.

The following is example how to use the script with certbot's DNS validation:
```
export CERT_FQDN=example.com
export CERT_SAN=www.example.com
export CERT_EMAIL=certmaster@example.com
export CERT_DIR=/etc/certificates/namecheap

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
```

## Build a Multi-Arch Docker Image for certbot renewal
```
docker buildx build \
--push \
--tag $DOCKER_USERNAME/certbot-namecheap:latest \
-f Dockerfile.certbot \
--platform linux/amd64,linux/arm64 . 
```