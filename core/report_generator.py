from io import BytesIO
from typing import Dict, Any, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)


def _plotly_fig_to_png_bytes(fig) -> bytes:
    return fig.to_image(format="png", scale=2)


def _build_surge_rows(surge_specs: Dict[str, List[Any]]) -> List[List[str]]:
    rows = [["Unit", "Surge", "Start Day", "End Day", "Admissions/Day"]]
    for unit, surges in surge_specs.items():
        for idx, (t_on, t_off, amp) in enumerate(surges, start=1):
            rows.append([unit, str(idx), f"{t_on:.1f}", f"{t_off:.1f}", f"{amp:.1f}"])
    return rows


def _build_metric_rows(surge_metrics: Dict[str, Any]) -> List[List[str]]:
    rows = [
        ["Metric", "Value"],
        ["Peak Total Bed Demand", f"{surge_metrics['peak_extra_beds_total']:.1f}"],
        ["Surge Duration (days)", f"{surge_metrics['surge_duration_days']}"],
        ["Total Workload (bed-days)", f"{surge_metrics['extra_beddays_total_cut']:.1f}"],
    ]

    for unit, value in surge_metrics["peak_extra_beds_per_comp"].items():
        rows.append([f"Peak Extra Beds - {unit}", f"{value:.1f}"])

    for unit, value in surge_metrics["extra_beddays_per_comp_cut"].items():
        rows.append([f"Extra Bed-Days - {unit}", f"{value:.1f}"])

    return rows


def _build_capacity_rows(capacity_summary: Dict[str, Any]) -> List[List[str]]:
    rows = [["Unit", "Available Beds", "Peak Need", "Gap"]]
    peak_needs = capacity_summary.get("peak_extra_beds_per_comp", {})
    available_beds = capacity_summary.get("available_beds", {})
    capacity_deficit = capacity_summary.get("capacity_deficit", {})

    for unit in peak_needs:
        rows.append([
            unit,
            f"{available_beds.get(unit, 0):.0f}",
            f"{peak_needs.get(unit, 0):.1f}",
            f"{capacity_deficit.get(unit, 0):.1f}",
        ])

    return rows


def _styled_table(rows: List[List[str]]) -> Table:
    table = Table(rows, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9edf7")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return table


def build_surge_report_pdf(
    selected_units: List[str],
    surge_specs: Dict[str, List[Any]],
    results: Dict[str, Any],
    surge_metrics: Dict[str, Any],
    params: Dict[str, Any],
    simulation_end_days: float,
    fig,
    capacity_summary: Dict[str, Any] | None = None,
) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Hospital Surge Scenario Report", styles["Title"]))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph(
        f"Selected units: {', '.join(selected_units)}<br/>Simulation end: {simulation_end_days:.1f} days",
        styles["BodyText"],
    ))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("Surge Events", styles["Heading2"]))
    story.append(_styled_table(_build_surge_rows(surge_specs) if surge_specs else [["Unit", "Surge", "Start Day", "End Day", "Admissions/Day"], ["None", "-", "-", "-", "-"]]))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Summary Metrics", styles["Heading2"]))
    story.append(_styled_table(_build_metric_rows(surge_metrics)))
    story.append(Spacer(1, 0.2 * inch))

    if capacity_summary:
        story.append(Paragraph("Capacity Gap Assessment", styles["Heading2"]))
        story.append(_styled_table(_build_capacity_rows(capacity_summary)))
        story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Surge Response Plot", styles["Heading2"]))
    try:
        fig_bytes = _plotly_fig_to_png_bytes(fig)
        fig_buffer = BytesIO(fig_bytes)
        story.append(Image(fig_buffer, width=6.8 * inch, height=4.8 * inch))
    except Exception:
        story.append(Paragraph("Plot image could not be embedded in the PDF in this environment.", styles["BodyText"]))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Key Parameters", styles["Heading2"]))
    param_rows = [["Parameter", "Value"]]
    for key in sorted(params.keys()):
        value = params[key]
        if isinstance(value, (int, float)):
            param_rows.append([key, f"{value:.4f}"])
        else:
            param_rows.append([key, str(value)])
    story.append(_styled_table(param_rows[:25]))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
