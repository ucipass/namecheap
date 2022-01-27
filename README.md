# Namecheap Dynamic Update Script
This program has two use cases:
- Update namecheap DNS records using a YAML file
- Use it with letsencrypt certbot -manual-auth-hook and --manual-clean-up script to authenticate certificates.

# Mandatory environment variables
NAMECHEAP_USER=[USER]
NAMECHEAP_APIKEY=[APIKEY]
NAMECHEAP_SUBDOMAIN=[sub-domain e.g. example]
NAMECHEAP_TOPDOMAIN=[top level domain e.g com]

# Certbot update example (use --test-cert for testing)
certbot -d test.example.com \
--text --non-interactive --agree-tos --email postamster@example.com \
--config-dir ./certificates \
--work-dir   ./certificates \
--logs-dir   ./certificates  \
--manual-public-ip-logging-ok \
--manual-auth-hook    "./namecheap.py --add" \
--manual-cleanup-hook "./namecheap.py --delete"  \
--manual --preferred-challenges dns \
certonly

