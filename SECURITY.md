# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | ✅ Active  |
| 0.10.x  | ✅ Active  |
| 0.9.x   | ⚠️ Critical fixes only |
| < 0.9   | ❌ End of life |

## Reporting a Vulnerability

**Do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email:

📧 **kaliyugiheart@gmail.com**

Include the following in your report:
- Description of the vulnerability
- Steps to reproduce
- Impact assessment
- Suggested fix (if any)

### What to expect
- **Acknowledgment**: Within 48 hours
- **Assessment**: Within 1 week
- **Fix timeline**: Critical issues within 72 hours, others within 2 weeks
- **Credit**: You'll be credited in the release notes (unless you prefer anonymity)

## Playground Security

The MOL online playground at [https://mol.cruxlabx.in](https://mol.cruxlabx.in) runs in **sandbox mode** with:

- 26 dangerous functions blocked (file I/O, network, server, concurrency)
- 5-second execution timeout
- 30 requests/minute rate limiting per IP
- 10KB code size limit
- HTTPS with Let's Encrypt SSL
- Nginx reverse proxy with security headers

Full security policy available at: `GET /api/security`

## Responsible Disclosure

We follow responsible disclosure practices. If you discover a vulnerability:

1. Report it privately via the email above
2. Allow reasonable time for a fix before public disclosure
3. We'll coordinate the disclosure timeline with you

Thank you for helping keep MOL and its community safe.
