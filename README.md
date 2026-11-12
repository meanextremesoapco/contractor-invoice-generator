# Contractor Invoice Generator

Simple tool to automate **monthly contractor invoices**.

Generates clean, professional PDF invoices (and optional Markdown) from a YAML config file.

## Quick Start

1. Edit `config.yaml` with your details and the current month's work.
2. Run:

```bash
python generate_invoice.py
```

This creates:
- `invoices/Invoice-YYYY-MM.pdf`
- `invoices/Invoice-YYYY-MM.md` (optional)

## Requirements

- Python 3.9+
- `reportlab` and `PyYAML`

```bash
pip install reportlab pyyaml
```

## Configuration

Edit `config.yaml`:

```yaml
# Your details
contractor:
  name: "Your Name / Business"
  email: "you@example.com"
  address: |
    123 Main St
    City, ST 12345
  phone: "+1 (555) 123-4567"

# Client details
client:
  name: "Client Company Name"
  email: "ap@client.com"
  address: |
    456 Client Ave
    City, ST 67890

# Invoice settings
invoice:
  number_prefix: "INV"          # becomes INV-2026-11
  currency: "USD"
  payment_terms: "Net 30"
  notes: |
    Thank you for the opportunity to work with you.
    Payment can be made via ACH or check.

# Current period work
period:
  start: "2026-11-01"
  end: "2026-11-30"
  description: "Software development & consulting services"

# Billing method — choose one
billing:
  type: "hourly"                # "hourly" or "fixed"
  hourly_rate: 125.00
  hours: 68.5
  # fixed_amount: 8500.00       # use this instead if type: fixed
```

## Features

- Clean professional PDF layout
- Automatic invoice numbering (`INV-YYYY-MM`)
- Supports both hourly and fixed-fee billing
- Optional Markdown output for easy emailing / editing
- All configuration in one simple YAML file

## License

MIT — free to use and modify.
