"""Slack alert stub for drill events and DAG failures.

Sends a structured message to a Slack webhook when:
  - A DAG task fails (called from an Airflow on_failure_callback or a monitoring job)
  - An MTTR drill event is recorded (called from check_isolation.py or manually)

Fasa 1: this is a syntax-valid stub. The webhook URL is not configured; calling send_alert()
will raise ConfigurationError if SLACK_WEBHOOK_URL is not set. Wire up at Fasa 3 alongside
the MWAA deployment.

Usage (Fasa 3+):
    from observability.alerts.slack_alert import send_alert
    send_alert(event="dag_failure", dag_id="home_credit_trigger", details="GlueJobOperator failed")
"""
from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone


class ConfigurationError(Exception):
    pass


@dataclass
class AlertPayload:
    event: str
    dag_id: str
    details: str
    severity: str = "WARNING"
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_slack_blocks(self) -> dict:
        severity_emoji = {"INFO": ":information_source:", "WARNING": ":warning:", "CRITICAL": ":red_circle:"}.get(
            self.severity, ":grey_question:"
        )
        return {
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": f"{severity_emoji} Control-Plane Alert — {self.event}"},
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*DAG:*\n`{self.dag_id}`"},
                        {"type": "mrkdwn", "text": f"*Severity:*\n{self.severity}"},
                        {"type": "mrkdwn", "text": f"*Time:*\n{self.timestamp}"},
                        {"type": "mrkdwn", "text": f"*Details:*\n{self.details}"},
                    ],
                },
            ]
        }


def send_alert(event: str, dag_id: str, details: str, severity: str = "WARNING") -> None:
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        raise ConfigurationError(
            "SLACK_WEBHOOK_URL not set — Slack alerts require the webhook URL in the environment. "
            "See architecture/SECRETS_BACKEND.md for credential management conventions."
        )
    payload = AlertPayload(event=event, dag_id=dag_id, details=details, severity=severity)
    body = json.dumps(payload.to_slack_blocks()).encode("utf-8")
    req = urllib.request.Request(webhook_url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Slack webhook returned {resp.status}")


def send_mttr_event(fault_name: str, mttr_minutes: float, outcome: str) -> None:
    send_alert(
        event="mttr_drill",
        dag_id=f"simulation/{fault_name}",
        details=f"Drill complete — MTTR: {mttr_minutes:.1f} min, outcome: {outcome}",
        severity="INFO" if outcome == "GREEN" else "WARNING",
    )
