
from context_aware_suggestion_rag.interfaces.notification_provider import (
    NotificationProvider,
)


class FakeNotificationProvider(NotificationProvider):

    def __init__(self):
        self.sent_notifications = []

    def send(self, recipient, subject, message, metadata=None):
        self.sent_notifications.append({
            "recipient": recipient,
            "subject": subject,
            "message": message,
            "metadata": metadata or {},
        })
        return True

    def health_check(self):
        return True


def main():
    provider = FakeNotificationProvider()

    assert isinstance(provider, NotificationProvider)
    print("Notification provider inheritance: PASS")

    assert provider.health_check()
    print("Notification provider health check: PASS")

    result = provider.send(
        recipient="test@example.com",
        subject="Pipeline completed",
        message="Your workflow has completed.",
        metadata={"workflow_id": "wf_test"},
    )

    assert result is True
    assert len(provider.sent_notifications) == 1
    print("Notification sending interface: PASS")

    notification = provider.sent_notifications[0]

    assert notification["recipient"] == "test@example.com"
    assert notification["subject"] == "Pipeline completed"
    assert notification["metadata"]["workflow_id"] == "wf_test"
    print("Notification payload validation: PASS")

    provider.close()
    print("Notification provider close interface: PASS")

    print("\nAll notification provider interface tests passed.")


if __name__ == "__main__":
    main()
