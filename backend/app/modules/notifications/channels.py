import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class NotificationChannelSender:
    @staticmethod
    async def send_email(to_address: str, title: str, message: str):
        logger.info(f"[CHANNEL - EMAIL] Sending email to {to_address}: {title}")
        return True

    @staticmethod
    async def send_webhook(webhook_url: str, payload: Dict[str, Any]):
        logger.info(
            f"[CHANNEL - WEBHOOK] Dispatching HTTP POST webhook payload to {webhook_url}"
        )
        return True

    @staticmethod
    async def send_slack(slack_url: str, title: str, message: str):
        logger.info(
            f"[CHANNEL - SLACK] Posting Slack alert message to {slack_url}: {title}"
        )
        return True

    @staticmethod
    async def send_teams(teams_url: str, title: str, message: str):
        logger.info(
            f"[CHANNEL - TEAMS] Posting Microsoft Teams Adaptive Card to {teams_url}: {title}"
        )
        return True
