import csv
import io

from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import gettext as _
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from apps.accounts.models import StaffUnavailability


def _event_rows(events):
    return [
        [
            event.planned_date.strftime("%Y-%m"),
            event.title,
            event.planned_date,
            event.start_time.strftime("%H:%M"),
            event.venue.localized_name,
            event.get_status_display(),
            event.expected_attendees,
            event.attendances.count(),
        ]
        for event in events
    ]


def _attendee_rows(events):
    rows = []
    for event in events.prefetch_related("attendances"):
        for attendance in event.attendances.all():
            rows.append(
                [
                    event.planned_date.strftime("%Y-%m"),
                    event.title,
                    event.planned_date,
                    attendance.attendee_name,
                    attendance.attendee_organization,
                    attendance.attendee_role,
                    attendance.get_checkin_method_display(),
                    timezone.localtime(attendance.checked_in_at).strftime("%Y-%m-%d %H:%M"),
                ]
            )
    return rows


def _busy_staff_rows(start, end):
    slots = (
        StaffUnavailability.objects.filter(start_date__lte=end, end_date__gte=start)
        .select_related("user")
        .order_by("start_date", "start_time")
    )
    return [
        [
            slot.user.get_full_name() or slot.user.username,
            slot.start_date,
            slot.start_time.strftime("%H:%M"),
            slot.end_date,
            slot.end_time.strftime("%H:%M"),
            slot.reason,
        ]
        for slot in slots
    ]


def csv_response(events, report, kind="events"):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="iems-report-events.csv"'
    response.write("\ufeff")
    writer = csv.writer(response)
    datasets = {
        "events": (
            [
                _("Month"),
                _("Event"),
                _("Date"),
                _("Time"),
                _("Venue"),
                _("Status"),
                _("Expected attendees"),
                _("Checked in"),
            ],
            _event_rows(events),
        ),
        "venues": (
            [
                _("Venue"),
                _("Available minutes"),
                _("Booked minutes"),
                _("Utilization %"),
                _("Events"),
            ],
            [
                [
                    r["name"],
                    r["available_minutes"],
                    r["booked_minutes"],
                    r["utilization"],
                    r["event_count"],
                ]
                for r in report["venues"]
            ],
        ),
        "attendance": (
            [_("Metric"), _("Value")],
            [[k, v] for k, v in report["attendance"].items() if not isinstance(v, list)],
        ),
        "approvals": (
            [_("Metric"), _("Value")],
            [[k, v] for k, v in report["approvals"].items() if not isinstance(v, dict)],
        ),
        "publications": (
            [_("Metric"), _("Value")],
            [
                [key, value]
                for key, value in report["publications"].items()
                if not isinstance(value, dict | list | tuple | set)
            ],
        ),
    }
    headers, rows = datasets.get(kind, datasets["events"])
    writer.writerow(headers)
    writer.writerows(rows)
    return response


def _sheet(workbook, title, headers, rows):
    sheet = workbook.create_sheet(title=title)
    sheet.append(headers)
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="F8FAFC")
        cell.fill = PatternFill("solid", fgColor="07172F")
    for row in rows:
        sheet.append(row)
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for column in range(1, len(headers) + 1):
        values = [
            str(sheet.cell(row=row, column=column).value or "")
            for row in range(1, sheet.max_row + 1)
        ]
        sheet.column_dimensions[get_column_letter(column)].width = min(
            max(map(len, values)) + 2, 48
        )
    return sheet


def xlsx_response(events, report):
    workbook = Workbook()
    workbook.remove(workbook.active)
    summary_rows = [
        [key.replace("_", " ").title(), value] for key, value in report["summary"].items()
    ]
    _sheet(workbook, _("Summary"), [_("Metric"), _("Value")], summary_rows)
    headers = [
        _("Month"),
        _("Event"),
        _("Date"),
        _("Time"),
        _("Venue"),
        _("Status"),
        _("Expected"),
        _("Checked in"),
    ]
    _sheet(workbook, _("Events"), headers, _event_rows(events))
    _sheet(
        workbook,
        _("Attendees"),
        [
            _("Month"),
            _("Event"),
            _("Date"),
            _("Attendee"),
            _("Organization"),
            _("Role"),
            _("Check-in method"),
            _("Checked in at"),
        ],
        _attendee_rows(events),
    )
    _sheet(
        workbook,
        _("Busy staff"),
        [_("Staff"), _("Start date"), _("Start time"), _("End date"), _("End time"), _("Reason")],
        _busy_staff_rows(report["start"], report["end"]),
    )
    _sheet(
        workbook,
        _("Venues"),
        [_("Venue"), _("Available minutes"), _("Booked minutes"), _("Utilization %"), _("Events")],
        [
            [
                r["name"],
                r["available_minutes"],
                r["booked_minutes"],
                r["utilization"],
                r["event_count"],
            ]
            for r in report["venues"]
        ],
    )
    _sheet(
        workbook,
        _("Attendance"),
        [_("Metric"), _("Value")],
        [[k, v] for k, v in report["attendance"].items() if not isinstance(v, list)],
    )
    _sheet(
        workbook,
        _("Approvals"),
        [_("Metric"), _("Value")],
        [[k, v] for k, v in report["approvals"].items() if not isinstance(v, dict)],
    )
    _sheet(
        workbook,
        _("Publications"),
        [_("Metric"), _("Value")],
        [
            [key, value]
            for key, value in report["publications"].items()
            if not isinstance(value, dict | list | tuple | set)
        ],
    )
    output = io.BytesIO()
    workbook.save(output)
    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="iems-report.xlsx"'
    return response


def pdf_response(report):
    output = io.BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )
    styles = getSampleStyleSheet()
    story = [
        Paragraph(_("IEMS Leadership Report"), styles["Title"]),
        Paragraph(f"{report['start']:%d.%m.%Y} – {report['end']:%d.%m.%Y}", styles["Normal"]),
        Paragraph(f"{_('Generated')}: {timezone.localtime():%d.%m.%Y %H:%M}", styles["Normal"]),
        Spacer(1, 8 * mm),
    ]
    summary = [[_("Metric"), _("Value")]] + [
        [key.replace("_", " ").title(), "—" if value is None else value]
        for key, value in report["summary"].items()
    ]
    table = Table(summary, colWidths=(90 * mm, 45 * mm), repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#07172F")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#F8FAFC")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.extend([table, PageBreak(), Paragraph(_("Venue utilization"), styles["Heading1"])])
    venue_rows = [[_("Venue"), _("Booked minutes"), _("Utilization %"), _("Events")]] + [
        [row["name"], row["booked_minutes"], row["utilization"], row["event_count"]]
        for row in report["venues"]
    ]
    story.append(Table(venue_rows, repeatRows=1))
    for title, section in (
        (_("Attendance"), report["attendance"]),
        (_("Approval performance"), report["approvals"]),
        (_("Publication status"), report["publications"]),
    ):
        story.extend(
            [
                Spacer(1, 7 * mm),
                Paragraph(title, styles["Heading2"]),
                Table(
                    [[_("Metric"), _("Value")]]
                    + [
                        [key.replace("_", " ").title(), "—" if value is None else value]
                        for key, value in section.items()
                        if not isinstance(value, list | dict)
                    ],
                    repeatRows=1,
                ),
            ]
        )
    document.build(story)
    response = HttpResponse(output.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="iems-leadership-report.pdf"'
    return response
