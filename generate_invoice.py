#!/usr/bin/env python3
"""
Contractor Invoice Generator
Generates a clean professional PDF (and optional Markdown) invoice
from a simple YAML config file.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def calculate_total(billing: dict) -> tuple[float, str]:
    """Return (total_amount, description_line)"""
    if billing.get("type") == "fixed":
        amount = float(billing["fixed_amount"])
        desc = "Fixed fee for the period"
        return amount, desc

    # default to hourly
    rate = float(billing["hourly_rate"])
    hours = float(billing["hours"])
    amount = rate * hours
    desc = f"{hours:.2f} hours @ ${rate:,.2f}/hr"
    return amount, desc


def format_currency(amount: float, currency: str = "USD") -> str:
    if currency.upper() == "USD":
        return f"${amount:,.2f}"
    return f"{amount:,.2f} {currency}"


def generate_pdf(cfg: dict, output_path: Path) -> None:
    contractor = cfg["contractor"]
    client = cfg["client"]
    inv = cfg["invoice"]
    period = cfg["period"]
    billing = cfg["billing"]

    total, line_desc = calculate_total(billing)
    currency = inv.get("currency", "USD")

    # Invoice number: INV-2026-11
    start = datetime.strptime(period["start"], "%Y-%m-%d")
    invoice_number = f"{inv.get('number_prefix', 'INV')}-{start.strftime('%Y-%m')}"

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="TitleBig",
            parent=styles["Heading1"],
            fontSize=22,
            spaceAfter=4,
            textColor=colors.HexColor("#1a1a1a"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHead",
            parent=styles["Heading2"],
            fontSize=11,
            spaceBefore=14,
            spaceAfter=6,
            textColor=colors.HexColor("#333333"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Right",
            parent=styles["Normal"],
            fontSize=10,
            alignment=TA_RIGHT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallGray",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#555555"),
            leading=12,
        )
    )

    story = []

    # Header
    story.append(Paragraph("INVOICE", styles["TitleBig"]))
    story.append(Spacer(1, 6))

    # Invoice meta + contractor info side by side
    header_data = [
        [
            Paragraph(
                f"<b>{contractor['name']}</b><br/>"
                + contractor.get("address", "").replace("\n", "<br/>")
                + f"<br/>{contractor.get('email', '')}"
                + (f"<br/>{contractor['phone']}" if contractor.get("phone") else ""),
                styles["Body"],
            ),
            Paragraph(
                f"<b>Invoice #:</b> {invoice_number}<br/>"
                f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}<br/>"
                f"<b>Period:</b> {period['start']} → {period['end']}<br/>"
                f"<b>Terms:</b> {inv.get('payment_terms', 'Net 30')}",
                styles["Right"],
            ),
        ]
    ]

    header_table = Table(header_data, colWidths=[3.8 * inch, 3.2 * inch])
    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.append(header_table)
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))

    # Bill To
    story.append(Paragraph("BILL TO", styles["SectionHead"]))
    story.append(
        Paragraph(
            f"<b>{client['name']}</b><br/>"
            + client.get("address", "").replace("\n", "<br/>")
            + f"<br/>{client.get('email', '')}",
            styles["Body"],
        )
    )

    # Line items
    story.append(Paragraph("SERVICES", styles["SectionHead"]))

    desc = period.get("description", "Professional services")
    amount_str = format_currency(total, currency)

    data = [
        ["Description", "Amount"],
        [f"{desc}<br/><font size='8' color='#666666'>{line_desc}</font>", amount_str],
        ["", ""],
        ["Total Due", amount_str],
    ]

    # Convert description cells to Paragraphs so HTML works
    table_data = []
    for i, row in enumerate(data):
        if i == 1:
            table_data.append(
                [
                    Paragraph(row[0], styles["Body"]),
                    Paragraph(row[1], styles["Right"]),
                ]
            )
        else:
            table_data.append(
                [
                    Paragraph(f"<b>{row[0]}</b>" if i in (0, 3) else row[0], styles["Body"]),
                    Paragraph(f"<b>{row[1]}</b>" if i == 3 else row[1], styles["Right"]),
                ]
            )

    col_widths = [5.2 * inch, 1.8 * inch]
    t = Table(table_data, colWidths=col_widths)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#333333")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 1), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
                ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor("#cccccc")),
                ("LINEABOVE", (0, 3), (-1, 3), 1, colors.HexColor("#333333")),
                ("BACKGROUND", (0, 3), (-1, 3), colors.HexColor("#f8f8f8")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(t)

    # Notes
    if inv.get("notes"):
        story.append(Spacer(1, 18))
        story.append(Paragraph("NOTES", styles["SectionHead"]))
        notes_text = inv["notes"].strip().replace("\n", "<br/>")
        story.append(Paragraph(notes_text, styles["SmallGray"]))

    # Footer
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#dddddd")))
    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} • {invoice_number}",
            styles["SmallGray"],
        )
    )

    doc.build(story)
    print(f"✅ PDF created: {output_path}")


def generate_markdown(cfg: dict, output_path: Path) -> None:
    contractor = cfg["contractor"]
    client = cfg["client"]
    inv = cfg["invoice"]
    period = cfg["period"]
    billing = cfg["billing"]

    total, line_desc = calculate_total(billing)
    currency = inv.get("currency", "USD")
    start = datetime.strptime(period["start"], "%Y-%m-%d")
    invoice_number = f"{inv.get('number_prefix', 'INV')}-{start.strftime('%Y-%m')}"

    md = f"""# INVOICE

**Invoice #:** {invoice_number}  
**Date:** {datetime.now().strftime('%B %d, %Y')}  
**Period:** {period['start']} → {period['end']}  
**Payment Terms:** {inv.get('payment_terms', 'Net 30')}

---

### From
**{contractor['name']}**  
{contractor.get('address', '').strip()}  
{contractor.get('email', '')}  
{contractor.get('phone', '')}

### Bill To
**{client['name']}**  
{client.get('address', '').strip()}  
{client.get('email', '')}

---

### Services

| Description | Amount |
|-------------|--------|
| {period.get('description', 'Professional services')}<br><small>{line_desc}</small> | **{format_currency(total, currency)}** |
| **Total Due** | **{format_currency(total, currency)}** |

"""

    if inv.get("notes"):
        md += "\n### Notes\n\n" + inv["notes"].strip() + "\n"

    md += "\n---\n*Generated " + datetime.now().strftime("%Y-%m-%d %H:%M") + "*\n"

    output_path.write_text(md, encoding="utf-8")
    print(f"✅ Markdown created: {output_path}")


def main() -> None:
    cfg = load_config("config.yaml")

    # Create output directory
    out_dir = Path("invoices")
    out_dir.mkdir(exist_ok=True)

    start = datetime.strptime(cfg["period"]["start"], "%Y-%m-%d")
    prefix = cfg["invoice"].get("number_prefix", "INV")
    base_name = f"{prefix}-{start.strftime('%Y-%m')}"

    pdf_path = out_dir / f"{base_name}.pdf"
    md_path = out_dir / f"{base_name}.md"

    generate_pdf(cfg, pdf_path)
    generate_markdown(cfg, md_path)

    print("\nDone. Update config.yaml next month and run again.")


if __name__ == "__main__":
    main()
