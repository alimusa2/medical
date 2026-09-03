import os
import re
import html
import json
from datetime import datetime
from typing import Dict, Any, List

from config import settings

def _get_reportlab():
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
    return {
        "letter": letter,
        "SimpleDocTemplate": SimpleDocTemplate,
        "Paragraph": Paragraph,
        "Spacer": Spacer,
        "Table": Table,
        "TableStyle": TableStyle,
        "HRFlowable": HRFlowable,
        "KeepTogether": KeepTogether,
        "getSampleStyleSheet": getSampleStyleSheet,
        "ParagraphStyle": ParagraphStyle,
        "colors": colors,
        "canvas": canvas
    }

def clean_text_for_pdf(text: Any) -> str:
    """
    Sanitize text strings for ReportLab PDF generation:
    - Converts input to string safely.
    - Replaces unicode symbols and emojis that are not supported by standard Helvetica.
    - Strips raw markdown syntax (**bold**, *italic*, etc.).
    - Escapes XML special characters (&, <, >) to avoid Paragraph parsing crashes.
    """
    if text is None:
        return ""
    text = str(text)
    
    replacements = {
        "⚠️": "[!]",
        "✓": "[PASS]",
        "❌": "[FAIL]",
        "±": "+/-",
        "°C": " deg C",
        "°F": " deg F",
        "°": " deg",
        "µA": "uA",
        "µV": "uV",
        "µL": "uL",
        "µ": "u",
        "Ω": " ohm",
        "Ω": " ohm",
        "≤": "<=",
        "≥": ">=",
        "—": " - ",
        "–": " - ",
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "…": "...",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
        
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    
    text = html.escape(text, quote=False)
    return text.strip()


class PDFReportGenerator:
    @staticmethod
    def generate_evaluation_pdf(evaluation_id: int, eval_data: Dict[str, Any], output_filename: str = None) -> str:
        rl = _get_reportlab()
        letter = rl["letter"]
        SimpleDocTemplate = rl["SimpleDocTemplate"]
        Paragraph = rl["Paragraph"]
        Spacer = rl["Spacer"]
        Table = rl["Table"]
        TableStyle = rl["TableStyle"]
        HRFlowable = rl["HRFlowable"]
        KeepTogether = rl["KeepTogether"]
        getSampleStyleSheet = rl["getSampleStyleSheet"]
        ParagraphStyle = rl["ParagraphStyle"]
        colors = rl["colors"]
        canvas = rl["canvas"]

        class NumberedCanvas(canvas.Canvas):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._saved_page_states = []

            def showPage(self):
                self._saved_page_states.append(dict(self.__dict__))
                self._startPage()

            def save(self):
                num_pages = len(self._saved_page_states)
                for state in self._saved_page_states:
                    self.__dict__.update(state)
                    self.draw_page_decorations(num_pages)
                    super().showPage()
                super().save()

            def draw_page_decorations(self, page_count: int):
                self.saveState()
                self.setFont("Helvetica", 8)
                self.setFillColor(colors.HexColor("#64748b"))
                if self._pageNumber > 1:
                    self.drawString(36, 762, "MedVerify AI — Medical Device TRF Evaluation Report")
                    self.drawRightString(576, 762, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
                    self.setStrokeColor(colors.HexColor("#cbd5e1"))
                    self.setLineWidth(0.5)
                    self.line(36, 754, 576, 754)
                self.setStrokeColor(colors.HexColor("#cbd5e1"))
                self.setLineWidth(0.5)
                self.line(36, 36, 576, 36)
                self.drawString(36, 24, "PROTOTYPE DECISION-SUPPORT REPORT  |  NOT FOR REGULATORY CERTIFICATION")
                self.drawRightString(576, 24, f"Page {self._pageNumber} of {page_count}")
                self.restoreState()

        if not output_filename:
            output_filename = f"MedVerify_TRF_Evaluation_Report_{evaluation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        file_path = os.path.join(settings.REPORT_DIR, output_filename)
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=48,
            bottomMargin=48
        )

        styles = getSampleStyleSheet()

        c_primary = colors.HexColor("#0f172a")     # Slate 900
        c_brand = colors.HexColor("#0284c7")       # Sky 600
        c_text = colors.HexColor("#334155")        # Slate 700
        c_disclaimer = colors.HexColor("#b91c1c")  # Red 700
        c_border = colors.HexColor("#cbd5e1")      # Slate 300

        title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=17, leading=21, textColor=c_primary, spaceAfter=4, fontName="Helvetica-Bold")
        subtitle_style = ParagraphStyle('DocSubtitle', parent=styles['Normal'], fontSize=9, leading=12, textColor=c_brand, spaceAfter=6, fontName="Helvetica")
        section_style = ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontSize=10.5, leading=14, textColor=c_primary, spaceBefore=10, spaceAfter=5, fontName="Helvetica-Bold")
        body_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], fontSize=8, leading=11, textColor=c_text, fontName="Helvetica")
        disclaimer_style = ParagraphStyle('DisclaimerText', parent=styles['Normal'], fontSize=8, leading=11, textColor=c_disclaimer, spaceBefore=4, spaceAfter=6, fontName="Helvetica")

        story = []

        # 1. Header & Title Banner
        story.append(Paragraph("MedVerify AI — Medical Device TRF Evaluation Report", title_style))
        story.append(Paragraph(f"Report Reference ID: EVAL-REC-{evaluation_id:05d}  |  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
        story.append(Paragraph(
            "<b>PROTOTYPE DISCLAIMER:</b> This report provides an automated preliminary evaluation based on the uploaded TRF "
            "and prototype standards knowledge base. It is intended for decision-support and demonstration purposes only. "
            "It does not constitute regulatory certification or formal compliance approval.",
            disclaimer_style
        ))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0"), spaceAfter=8))

        # 2. Overall Status Banner
        raw_status = eval_data.get("overall_status", "NEEDS REVIEW")
        if raw_status == "PASS":
            bg_color = colors.HexColor("#dcfce7")
            text_color = colors.HexColor("#14532d")
            border_color = colors.HexColor("#86efac")
            banner_text = "PRELIMINARY EVALUATION: PASS — Applicable TRF Evidence Satisfies Baseline Criteria"
        elif raw_status == "FAIL":
            bg_color = colors.HexColor("#fee2e2")
            text_color = colors.HexColor("#7f1d1d")
            border_color = colors.HexColor("#fca5a5")
            banner_text = "PRELIMINARY EVALUATION: FAIL — One or More Reported Measurements Exceed Safety Thresholds"
        else:
            bg_color = colors.HexColor("#fef3c7")
            text_color = colors.HexColor("#78350f")
            border_color = colors.HexColor("#fcd34d")
            banner_text = "PRELIMINARY EVALUATION: NEEDS REVIEW — Missing Evidence or Certifier Inspection Required"

        banner_style = ParagraphStyle('BannerText', parent=styles['Normal'], fontSize=9, leading=12, textColor=text_color, fontName="Helvetica-Bold", alignment=1)
        banner_table = Table([[Paragraph(clean_text_for_pdf(banner_text), banner_style)]], colWidths=[540])
        banner_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_color),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('PADDING', (0,0), (-1,-1), 6),
            ('BOX', (0,0), (-1,-1), 1, border_color)
        ]))
        story.append(banner_table)
        story.append(Spacer(1, 8))

        # 3. Device Metadata
        story.append(Paragraph("1. Device & Document Specifications", section_style))
        device_meta = eval_data.get("device_info", {})
        doc_meta = eval_data.get("document_info", {})

        meta_grid = [
            ["Device Name:", clean_text_for_pdf(device_meta.get("name", "N/A")), "Model Number:", clean_text_for_pdf(device_meta.get("model", "N/A"))],
            ["Manufacturer:", clean_text_for_pdf(device_meta.get("manufacturer", "N/A")), "Device Category:", clean_text_for_pdf(eval_data.get("device_type_name", device_meta.get("device_type", "N/A")))],
            ["Safety Pathway:", clean_text_for_pdf(eval_data.get("pathway", "ME Equipment")), "Batch Reference:", clean_text_for_pdf(eval_data.get("batch_id", "N/A"))],
            ["Source TRF File:", clean_text_for_pdf(doc_meta.get("filename", "N/A")), "Upload Date:", clean_text_for_pdf(doc_meta.get("upload_date", "N/A"))]
        ]
        t_meta = Table(meta_grid, colWidths=[105, 165, 105, 165])
        t_meta.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor("#64748b")),
            ('TEXTCOLOR', (2,0), (2,-1), colors.HexColor("#64748b")),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(t_meta)
        story.append(Spacer(1, 8))

        # 4. Summary Statistics
        story.append(Paragraph("2. Evaluation Summary Statistics", section_style))
        counts = eval_data.get("counts", {})
        stats_table_data = [
            ["Total Evaluated", "Passed Items", "Failed Items", "Needs Review", "Not Applicable"],
            [
                str(counts.get("total_tests", 0)),
                str(counts.get("passed_tests", 0)),
                str(counts.get("failed_tests", 0)),
                str(counts.get("needs_review_tests", 0)),
                str(counts.get("not_applicable_tests", 0))
            ]
        ]
        t_stats = Table(stats_table_data, colWidths=[108, 108, 108, 108, 108])
        t_stats.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8.5),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, c_border),
            ('PADDING', (0,0), (-1,-1), 4),
            ('TEXTCOLOR', (1,1), (1,1), colors.HexColor("#15803d")), # Green
            ('TEXTCOLOR', (2,1), (2,1), colors.HexColor("#b91c1c")), # Red
            ('TEXTCOLOR', (3,1), (3,1), colors.HexColor("#b45309")), # Amber
            ('TEXTCOLOR', (4,1), (4,1), colors.HexColor("#64748b")), # Slate
        ]))
        story.append(t_stats)
        story.append(Spacer(1, 8))

        # 5. Itemized Standards Comparison Table
        story.append(Paragraph("3. Standard Requirement Area vs TRF Evidence Comparison", section_style))
        table_rows = [["Standard", "Requirement Area", "TRF Evidence", "System Evaluation", "Evaluation Rationale"]]

        results_list = eval_data.get("results", [])
        for res in results_list:
            st = clean_text_for_pdf(res.get("status", "NEEDS REVIEW"))
            if st == "PASS":
                st_color = "#15803d"
            elif st == "FAIL":
                st_color = "#b91c1c"
            elif st == "NOT APPLICABLE":
                st_color = "#64748b"
            else:
                st_color = "#b45309"

            std_p = Paragraph(f"<b>{clean_text_for_pdf(res.get('standard_code', 'IEC 60601-1'))}</b><br/><font size=7 color='#64748b'>{clean_text_for_pdf(res.get('standard_category', 'General'))}</font>", body_style)
            test_p = Paragraph(clean_text_for_pdf(res.get("test_name", "N/A")), body_style)
            obs_str = f"Extracted: {res.get('observed_value', 'N/A')} {res.get('unit', '')}".strip()
            obs_p = Paragraph(clean_text_for_pdf(obs_str), body_style)
            st_paragraph = Paragraph(f"<b><font color='{st_color}'>{st}</font></b>", body_style)
            reason_p = Paragraph(clean_text_for_pdf(res.get("reason", "N/A")), body_style)

            table_rows.append([std_p, test_p, obs_p, st_paragraph, reason_p])

        t_results = Table(table_rows, colWidths=[90, 115, 95, 75, 165])

        t_style_rules = [
            ('BACKGROUND', (0,0), (-1,0), c_primary),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 7.5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('PADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]
        for row_idx in range(1, len(table_rows)):
            bg = colors.white if row_idx % 2 != 0 else colors.HexColor("#f8fafc")
            t_style_rules.append(('BACKGROUND', (0, row_idx), (-1, row_idx), bg))

        t_results.setStyle(TableStyle(t_style_rules))
        story.append(t_results)
        story.append(Spacer(1, 10))

        # 6. AI Evaluation Summary
        story.append(Paragraph("4. AI-Assisted Evaluation Summary", section_style))
        ai_data = eval_data.get("ai_summary", {})
        if isinstance(ai_data, str):
            try:
                ai_data = json.loads(ai_data)
            except Exception:
                ai_data = {"summary": ai_data, "key_findings": [], "recommendation": "Technical reviewer inspection required."}

        raw_summary = ai_data.get('summary', 'Evaluation completed.')
        raw_rec = ai_data.get('recommendation', 'Certifier review recommended.')

        summary_p = Paragraph(f"<b>Executive Summary:</b> {clean_text_for_pdf(raw_summary)}", body_style)
        rec_p = Paragraph(f"<b>Recommended Action:</b> {clean_text_for_pdf(raw_rec)}", body_style)

        ai_box_content = [[summary_p]]
        key_findings = ai_data.get("key_findings", [])
        if key_findings and isinstance(key_findings, list) and len(key_findings) > 0:
            findings_text = "<b>Key Assessment Findings:</b><br/>" + "<br/>".join([f"• {clean_text_for_pdf(f)}" for f in key_findings])
            ai_box_content.append([Spacer(1, 3)])
            ai_box_content.append([Paragraph(findings_text, body_style)])

        ai_box_content.append([Spacer(1, 3)])
        ai_box_content.append([rec_p])

        t_ai = Table(ai_box_content, colWidths=[540])
        t_ai.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
            ('PADDING', (0,0), (-1,-1), 6)
        ]))
        story.append(t_ai)
        story.append(Spacer(1, 10))

        # 7. Sign-off Block
        story.append(KeepTogether([
            Paragraph("5. Technical Reviewer Sign-Off", section_style),
            Spacer(1, 3),
            Table([
                ["Technical Reviewer:", "___________________________", "Date:", "_______________"],
                ["Authorized Certifier:", "___________________________", "Decision:", "[  ] ACCEPT   [  ] REJECT"]
            ], colWidths=[120, 200, 80, 140], style=[
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#334155")),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6)
            ])
        ]))

        doc.build(story, canvasmaker=NumberedCanvas)
        return file_path
