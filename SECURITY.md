# Security Policy

## Portfolio/demo status

ShopSphere is a portfolio/demo project. The local Docker configuration contains development-only credentials and must not be reused unchanged in production.

## Before production

- Generate a strong secret key and store it outside source control.
- Use HTTPS.
- Restrict CORS to trusted origins.
- Add rate limiting and abuse protection.
- Use secure cookies/token handling appropriate to the deployment.
- Rotate credentials and database passwords.
- Use managed PostgreSQL with backups and monitoring.
- Validate and normalize all external retailer-feed data.

## Reporting

Do not publish sensitive vulnerabilities publicly. For a portfolio deployment, contact the repository owner privately with reproduction details.
