
from context_aware_suggestion_rag.security.models import (
    SecurityEventType,
    SecuritySeverity,
)
from context_aware_suggestion_rag.security.monitor import SecurityMonitor


def test_event_monitoring():
    monitor = SecurityMonitor()

    alert = monitor.record_event(
        SecurityEventType.AUTHENTICATION,
        SecuritySeverity.INFO,
        "User authenticated.",
        principal="user_1",
    )

    assert alert is None
    assert monitor.get_snapshot().total_events == 1

    print("Security event monitoring: PASS")


def test_high_severity_alert():
    monitor = SecurityMonitor()

    alert = monitor.record_event(
        SecurityEventType.ACCESS_DENIED,
        SecuritySeverity.HIGH,
        "Unauthorized access attempt.",
        principal="user_2",
    )

    assert alert is not None
    assert alert.severity == SecuritySeverity.HIGH
    assert alert.principal == "user_2"

    print("High-severity alert generation: PASS")


def test_critical_alert():
    monitor = SecurityMonitor()

    alert = monitor.record_event(
        SecurityEventType.SYSTEM,
        SecuritySeverity.CRITICAL,
        "Critical security failure.",
    )

    assert alert is not None
    assert alert.severity == SecuritySeverity.CRITICAL

    print("Critical alert generation: PASS")


def test_severity_filtering():
    monitor = SecurityMonitor()

    monitor.record_event(
        SecurityEventType.VALIDATION,
        SecuritySeverity.HIGH,
        "High event.",
    )

    monitor.record_event(
        SecurityEventType.SYSTEM,
        SecuritySeverity.CRITICAL,
        "Critical event.",
    )

    assert len(monitor.get_alerts()) == 2
    assert len(
        monitor.get_alerts(SecuritySeverity.CRITICAL)
    ) == 1

    print("Alert severity filtering: PASS")


def test_blocked_event_count():
    monitor = SecurityMonitor()

    monitor.record_event(
        SecurityEventType.ACCESS_DENIED,
        SecuritySeverity.HIGH,
        "Access denied.",
    )

    assert monitor.get_snapshot().blocked_events == 1

    print("Blocked event tracking: PASS")


def test_snapshot():
    monitor = SecurityMonitor()

    monitor.record_event(
        SecurityEventType.AUTHENTICATION,
        SecuritySeverity.INFO,
        "Authentication success.",
    )

    monitor.record_event(
        SecurityEventType.ACCESS_DENIED,
        SecuritySeverity.HIGH,
        "Access denied.",
    )

    snapshot = monitor.get_snapshot()

    assert snapshot.total_events == 2
    assert snapshot.alerts_generated == 1
    assert snapshot.events_by_severity["info"] == 1
    assert snapshot.events_by_severity["high"] == 1

    print("Security monitoring snapshot: PASS")


def test_clear_alerts():
    monitor = SecurityMonitor()

    monitor.record_event(
        SecurityEventType.SYSTEM,
        SecuritySeverity.CRITICAL,
        "Critical event.",
    )

    assert monitor.clear_alerts() == 1
    assert len(monitor.get_alerts()) == 0

    print("Alert clearing: PASS")


def test_health_and_close():
    monitor = SecurityMonitor()

    assert monitor.health_check() is True

    monitor.close()

    assert monitor.health_check() is False

    try:
        monitor.get_snapshot()
    except RuntimeError:
        pass
    else:
        raise AssertionError("Expected closed monitor to reject operations.")

    print("Security monitor shutdown: PASS")


if __name__ == "__main__":
    test_event_monitoring()
    test_high_severity_alert()
    test_critical_alert()
    test_severity_filtering()
    test_blocked_event_count()
    test_snapshot()
    test_clear_alerts()
    test_health_and_close()

    print("\nAll security monitor tests passed.")
