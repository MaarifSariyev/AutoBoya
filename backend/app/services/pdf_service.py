import io
from datetime import datetime
from decimal import Decimal
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from app.schemas.calculation import CalculationResponse


class PDFService:
    @staticmethod
    def generate_formula_sheet_pdf(calc_data: CalculationResponse, preparation_notes: str = None) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0f172a"),
            alignment=1,  # Centered
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#475569"),
            alignment=1,
        )
        section_style = ParagraphStyle(
            "SectionHeader",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=12,
            spaceAfter=6,
        )
        normal_style = styles["Normal"]
        bold_style = ParagraphStyle("Bold", parent=styles["Normal"], fontName="Helvetica-Bold")

        story = []

        # Header Title
        story.append(Paragraph("AUTOMOTIVE REFINISH FORMULA SHEET", title_style))
        story.append(Paragraph("Azerbaijan Automotive Paint & Refinish Platform", subtitle_style))
        story.append(Spacer(1, 14))

        # Vehicle & Color Info Table
        brand_str = calc_data.brand_name or "Generic"
        model_str = calc_data.model_name or "All Models"
        info_data = [
            [
                Paragraph("<b>Vehicle Brand:</b>", normal_style),
                Paragraph(brand_str, normal_style),
                Paragraph("<b>Color Code:</b>", normal_style),
                Paragraph(f"<font size='12'><b>{calc_data.color_code}</b></font>", normal_style),
            ],
            [
                Paragraph("<b>Vehicle Model:</b>", normal_style),
                Paragraph(model_str, normal_style),
                Paragraph("<b>Color Name:</b>", normal_style),
                Paragraph(calc_data.color_name, normal_style),
            ],
            [
                Paragraph("<b>Formula Variant:</b>", normal_style),
                Paragraph(calc_data.variant_name, normal_style),
                Paragraph("<b>Formula Version:</b>", normal_style),
                Paragraph(f"v{calc_data.version}", normal_style),
            ],
            [
                Paragraph("<b>Target Quantity:</b>", bold_style),
                Paragraph(f"<b>{calc_data.target_amount} {calc_data.unit}</b>", bold_style),
                Paragraph("<b>Date Generated:</b>", normal_style),
                Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M"), normal_style),
            ],
        ]

        info_table = Table(info_data, colWidths=[1.5 * inch, 2.0 * inch, 1.5 * inch, 2.2 * inch])
        info_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ])
        )
        story.append(info_table)
        story.append(Spacer(1, 14))

        # Component Table
        story.append(Paragraph("Preparation Component Quantities", section_style))
        comp_headers = ["#", "Code", "Component Description", "Quantity", "Cumulative Target", "Share %"]
        table_data = [comp_headers]

        for idx, comp in enumerate(calc_data.components, 1):
            table_data.append([
                str(idx),
                comp.component_code,
                comp.component_name,
                f"{comp.amount} {comp.unit}",
                f"{comp.cumulative_amount} {comp.unit}",
                f"{comp.percentage}%",
            ])

        # Total row
        table_data.append([
            "",
            "TOTAL",
            "Calculated Mix Total",
            f"{calc_data.total} {calc_data.unit}",
            "-",
            "100.0%",
        ])

        comp_table = Table(table_data, colWidths=[0.4 * inch, 1.0 * inch, 2.7 * inch, 1.1 * inch, 1.2 * inch, 0.8 * inch])
        comp_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e2e8f0")),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (3, 0), (-1, -1), "RIGHT"),
            ])
        )
        story.append(comp_table)
        story.append(Spacer(1, 14))

        # Notes section
        if preparation_notes:
            story.append(Paragraph("Preparation & Application Instructions", section_style))
            story.append(Paragraph(preparation_notes.replace("\n", "<br/>"), normal_style))
            story.append(Spacer(1, 10))

        # Workshop notice / Disclaimer
        disclaimer = (
            "<i>Notice: Shake tins thoroughly before pouring. Check color match with spray-out card before applying to vehicle. "
            "For professional workshop automotive refinish use only.</i>"
        )
        story.append(Paragraph(disclaimer, ParagraphStyle("Notice", parent=normal_style, fontSize=8, textColor=colors.HexColor("#64748b"))))

        doc.build(story)
        return buffer.getvalue()
