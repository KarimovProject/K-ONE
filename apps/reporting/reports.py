from apps.reporting.analytics import build_report, previous_range
from apps.reporting.forms import ReportFilterForm
from apps.reporting.selectors import filtered_events


def report_context(query, user):
    form = ReportFilterForm(query or {"period": "month"})
    if not form.is_valid():
        return form, None, None
    start, end = form.date_range()
    events = filtered_events(form.cleaned_data, start, end, user)
    previous_start, previous_end = previous_range(start, end)
    previous_events = filtered_events(form.cleaned_data, previous_start, previous_end, user)
    return form, events, build_report(
        events, start, end, form.cleaned_data, previous_events=previous_events
    )
