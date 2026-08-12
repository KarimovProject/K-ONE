from typing import TypedDict


class DashboardShellData(TypedDict):
    metrics: list[dict[str, str]]
    venues: list[dict[str, str]]


def get_dashboard_shell_data() -> DashboardShellData:
    """Return explicit Phase 0 placeholders without querying unfinished domains."""
    return {
        "metrics": [
            {"key": "today", "value": "—", "accent": "blue"},
            {"key": "upcoming", "value": "—", "accent": "cyan"},
            {"key": "active_halls", "value": "—", "accent": "emerald"},
            {"key": "pending", "value": "—", "accent": "amber"},
        ],
        "venues": [
            {"code": "ICH", "status": "placeholder"},
            {"code": "SSH", "status": "placeholder"},
            {"code": "INR", "status": "placeholder"},
            {"code": "EMR", "status": "placeholder"},
        ],
    }

