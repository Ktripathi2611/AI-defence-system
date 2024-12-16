import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiohttp
from aiohttp import web
import yaml

@dataclass
class AlertThreshold:
    metric: str
    warning_threshold: float
    critical_threshold: float
    duration: int  # Duration in seconds before alert is triggered
    cooldown: int  # Cooldown period in seconds before re-alerting

@dataclass
class Alert:
    id: str
    metric: str
    value: float
    threshold: float
    severity: str
    timestamp: str
    message: str
    acknowledged: bool = False

class AlertManager:
    def __init__(self, config_path: str = 'config/alert_config.yaml'):
        self.logger = self._setup_logger()
        self.thresholds: Dict[str, AlertThreshold] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.notification_channels: Dict[str, Dict[str, Any]] = {}
        self.metric_state: Dict[str, Dict[str, Any]] = {}
        self.load_config(config_path)

    def _setup_logger(self) -> logging.Logger:
        """Initialize logger for alert manager"""
        logger = logging.getLogger('alert_manager')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('alerts.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def load_config(self, config_path: str) -> None:
        """Load alert configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            # Load thresholds
            for threshold in config.get('thresholds', []):
                self.thresholds[threshold['metric']] = AlertThreshold(
                    metric=threshold['metric'],
                    warning_threshold=threshold['warning_threshold'],
                    critical_threshold=threshold['critical_threshold'],
                    duration=threshold.get('duration', 60),
                    cooldown=threshold.get('cooldown', 300)
                )

            # Load notification channels
            self.notification_channels = config.get('notification_channels', {})

        except Exception as e:
            self.logger.error(f'Error loading config: {str(e)}')
            raise

    async def check_metric(self, metric: str, value: float) -> None:
        """Check if a metric exceeds its thresholds"""
        if metric not in self.thresholds:
            return

        threshold = self.thresholds[metric]
        current_time = datetime.now()

        # Initialize metric state if not exists
        if metric not in self.metric_state:
            self.metric_state[metric] = {
                'first_exceeded': None,
                'last_alert': None,
                'current_severity': None
            }

        state = self.metric_state[metric]

        # Determine severity
        severity = None
        if value >= threshold.critical_threshold:
            severity = 'critical'
        elif value >= threshold.warning_threshold:
            severity = 'warning'

        if severity:
            if state['first_exceeded'] is None:
                state['first_exceeded'] = current_time
            elif (current_time - state['first_exceeded']).total_seconds() >= threshold.duration:
                if state['last_alert'] is None or \
                   (current_time - state['last_alert']).total_seconds() >= threshold.cooldown:
                    await self.create_alert(metric, value, severity)
                    state['last_alert'] = current_time
        else:
            # Reset state if metric is back to normal
            state['first_exceeded'] = None
            await self.resolve_alerts(metric)

    async def create_alert(self, metric: str, value: float, severity: str) -> None:
        """Create and send a new alert"""
        threshold = self.thresholds[metric]
        alert = Alert(
            id=f"{metric}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            metric=metric,
            value=value,
            threshold=threshold.critical_threshold if severity == 'critical' else threshold.warning_threshold,
            severity=severity,
            timestamp=datetime.now().isoformat(),
            message=f"{severity.upper()}: {metric} is {value}, threshold: {threshold.critical_threshold if severity == 'critical' else threshold.warning_threshold}"
        )

        self.active_alerts[alert.id] = alert
        self.alert_history.append(alert)
        self.logger.info(f'Created alert: {alert.message}')

        # Send notifications
        await self.send_notifications(alert)

    async def resolve_alerts(self, metric: str) -> None:
        """Resolve all active alerts for a metric"""
        resolved = []
        for alert_id, alert in self.active_alerts.items():
            if alert.metric == metric:
                alert.acknowledged = True
                resolved.append(alert_id)

        for alert_id in resolved:
            del self.active_alerts[alert_id]

    async def send_notifications(self, alert: Alert) -> None:
        """Send notifications through configured channels"""
        for channel, config in self.notification_channels.items():
            try:
                if channel == 'email':
                    await self.send_email_notification(alert, config)
                elif channel == 'webhook':
                    await self.send_webhook_notification(alert, config)
                elif channel == 'slack':
                    await self.send_slack_notification(alert, config)
            except Exception as e:
                self.logger.error(f'Error sending {channel} notification: {str(e)}')

    async def send_email_notification(self, alert: Alert, config: Dict[str, str]) -> None:
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = config['from_address']
            msg['To'] = config['to_address']
            msg['Subject'] = f"System Alert: {alert.severity.upper()} - {alert.metric}"

            body = f"""
            Alert Details:
            Metric: {alert.metric}
            Value: {alert.value}
            Threshold: {alert.threshold}
            Severity: {alert.severity}
            Time: {alert.timestamp}
            Message: {alert.message}
            """

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
                if config.get('use_tls', True):
                    server.starttls()
                if 'username' in config and 'password' in config:
                    server.login(config['username'], config['password'])
                server.send_message(msg)

        except Exception as e:
            self.logger.error(f'Error sending email: {str(e)}')
            raise

    async def send_webhook_notification(self, alert: Alert, config: Dict[str, str]) -> None:
        """Send webhook notification"""
        try:
            payload = {
                'alert_id': alert.id,
                'metric': alert.metric,
                'value': alert.value,
                'threshold': alert.threshold,
                'severity': alert.severity,
                'timestamp': alert.timestamp,
                'message': alert.message
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(config['url'], json=payload) as response:
                    if response.status >= 400:
                        raise Exception(f'Webhook request failed with status {response.status}')

        except Exception as e:
            self.logger.error(f'Error sending webhook: {str(e)}')
            raise

    async def send_slack_notification(self, alert: Alert, config: Dict[str, str]) -> None:
        """Send Slack notification"""
        try:
            color = '#ff0000' if alert.severity == 'critical' else '#ffa500'
            payload = {
                'attachments': [{
                    'color': color,
                    'title': f'System Alert: {alert.severity.upper()} - {alert.metric}',
                    'text': alert.message,
                    'fields': [
                        {'title': 'Metric', 'value': alert.metric, 'short': True},
                        {'title': 'Value', 'value': str(alert.value), 'short': True},
                        {'title': 'Threshold', 'value': str(alert.threshold), 'short': True},
                        {'title': 'Time', 'value': alert.timestamp, 'short': True}
                    ]
                }]
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(config['webhook_url'], json=payload) as response:
                    if response.status >= 400:
                        raise Exception(f'Slack webhook request failed with status {response.status}')

        except Exception as e:
            self.logger.error(f'Error sending Slack notification: {str(e)}')
            raise

    def get_active_alerts(self) -> List[Alert]:
        """Get list of active alerts"""
        return list(self.active_alerts.values())

    def get_alert_history(self, limit: Optional[int] = None) -> List[Alert]:
        """Get alert history with optional limit"""
        if limit:
            return self.alert_history[-limit:]
        return self.alert_history

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            return True
        return False
