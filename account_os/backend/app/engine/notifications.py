from typing import List, Dict, Any, Optional

class NotificationService:
    """
    Handles sending notifications through different channels.
    """
    @staticmethod
    async def send_notification(
        channel: str,
        recipient: str,
        title: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Sends a notification (mocked for now).
        """
        print(f"📢 [{channel.upper()}] to {recipient}: {title} - {message}")
        return True

    @staticmethod
    async def notify_approval_needed(user_email: str, tx_id: str, amount: float):
        await NotificationService.send_notification(
            channel="email",
            recipient=user_email,
            title="Approval Required",
            message=f"A transaction for {amount} requires your approval. ID: {tx_id}"
        )
        # Mock Slack/WhatsApp as well for Professional tier
        await NotificationService.send_notification(
            channel="slack",
            recipient="#accounting",
            title="Approval Required",
            message=f"TX {tx_id} for {amount} is pending approval."
        )
