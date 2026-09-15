# Security Policy

## Supported scope

This repository is a demonstration and research framework. It intentionally does not contain production credentials, private keys, account identifiers, or private configuration.

## Reporting a vulnerability

Please use GitHub private vulnerability reporting for security issues. Do not open a public issue containing secrets, account information, or exploit details.

## Secret handling rules

- Never commit API keys, private keys, seed phrases, passwords, cookies, or signing credentials.
- Use environment variables or a local secret manager for runtime credentials.
- Keep real datasets, account exports, order ledgers, and logs outside the repository.
- Run a secrets scanner before every public release.
- If a secret is committed, rotate it first, then remove it from Git history. History rewriting alone does not make an exposed secret safe.

## Public repository boundary

The production strategy, proprietary parameters and credentials are intentionally excluded from this repository.
