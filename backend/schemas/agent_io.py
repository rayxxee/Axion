"""Per-agent input/output Pydantic models."""

from __future__ import annotations

from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


# ──────────────────────────────────────────────
# Agent 1 — NewsParserAgent
# ──────────────────────────────────────────────

class EconomicSignal(BaseModel):
    signal: str
    magnitude: str
    direction: str = Field(
        ..., pattern=r"^(increase|decrease|neutral|uncertain)$"
    )


class NewsParserOutput(BaseModel):
    headline: str = Field(..., max_length=120)
    date: Optional[str] = None
    topic: str = Field(
        ...,
        pattern=r"^(monetary_policy|fiscal_policy|energy|trade|taxation|commodities|regulation|other)$",
    )
    key_entities: list[str]
    economic_signals: list[EconomicSignal]
    source_credibility_score: float = Field(..., ge=0.0, le=1.0)


# ──────────────────────────────────────────────
# Agent 2 — ImpactAnalyzerAgent
# ──────────────────────────────────────────────

class QuantifiedMetrics(BaseModel):
    cost_change_pkr: float
    margin_change_pct: float
    affected_orders_count: int = Field(..., ge=0, le=500)


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ImpactAnalyzerOutput(BaseModel):
    impact_summary: str
    affected_sectors: list[str]
    quantified_metrics: QuantifiedMetrics
    severity: Severity


# ──────────────────────────────────────────────
# Agent 3 — ActionGeneratorAgent
# ──────────────────────────────────────────────

class Action(BaseModel):
    rank: int = Field(..., ge=1, le=5)
    title: str = Field(..., max_length=80)
    rationale: str
    effort: str = Field(..., pattern=r"^(trivial|low|medium|high)$")
    impact: str = Field(
        ..., pattern=r"^(minimal|moderate|significant|transformative)$"
    )
    estimated_savings_pkr: float
    timeline_days: int = Field(..., ge=1, le=30)
    simulate: bool


class ActionGeneratorOutput(BaseModel):
    actions: list[Action] = Field(..., min_length=5, max_length=5)


# ──────────────────────────────────────────────
# Agent 4a — PricingUpdater
# ──────────────────────────────────────────────

class ProductUpdate(BaseModel):
    product_id: str
    product_name: str
    category: str
    unit: str
    before_price_pkr: float
    after_price_pkr: float
    change_pct: float
    effective_date: str
    justification: str


class PricingUpdaterOutput(BaseModel):
    simulation_type: str = "pricing_update"
    product_updates: list[ProductUpdate]
    summary: str


# ──────────────────────────────────────────────
# Agent 4b — NotificationDrafter
# ──────────────────────────────────────────────

class EmailTemplate(BaseModel):
    subject: str
    recipient_type: str
    body_html: str
    body_plain: str


class SmsTemplate(BaseModel):
    recipient_type: str
    message: str = Field(..., max_length=320)
    urdu_transliteration: str


class PushNotificationData(BaseModel):
    action_type: str
    severity: str
    deep_link: str


class PushNotification(BaseModel):
    title: str = Field(..., max_length=120)
    body: str = Field(..., max_length=300)
    data: PushNotificationData


class NotificationDrafterOutput(BaseModel):
    simulation_type: str = "notification"
    email_template: EmailTemplate
    sms_template: SmsTemplate
    push_notification: PushNotification


# ──────────────────────────────────────────────
# Agent 4c — WorkflowTriggerer
# ──────────────────────────────────────────────

class WorkflowAlert(BaseModel):
    alert_id: str
    type: str = Field(
        ...,
        pattern=r"^(approval_request|escalation|task_assignment|meeting_request|compliance_notice)$",
    )
    priority: str = Field(..., pattern=r"^(low|medium|high|urgent)$")
    recipient_role: str
    title: str
    description: str
    required_action: str
    deadline_hours: int
    auto_escalate_to: str


class WorkflowTriggererOutput(BaseModel):
    simulation_type: str = "workflow_trigger"
    alerts: list[WorkflowAlert]
    workflow_summary: str


# ──────────────────────────────────────────────
# Agent 4 — Combined Executor Output
# ──────────────────────────────────────────────

class ExecutorOutput(BaseModel):
    pricing: PricingUpdaterOutput
    notification: NotificationDrafterOutput
    workflow: WorkflowTriggererOutput


# ──────────────────────────────────────────────
# Agent 5 — OutputComposer / FinalReport
# ──────────────────────────────────────────────

class InsightCard(BaseModel):
    headline: str
    topic_badge: str
    severity_badge: str
    credibility_score: float
    one_liner: str


class ImpactMetricsCard(BaseModel):
    cost_change_pkr: float
    margin_change_pct: float
    affected_orders_count: int
    affected_sectors: list[str]
    risk_level: str


class ActionTaken(BaseModel):
    rank: int
    title: str
    status: str = Field(..., pattern=r"^(simulated|recommended)$")
    savings_pkr: float


class ExecutionLogEntry(BaseModel):
    timestamp: str
    agent: str
    action: str
    status: str
    details: str


class SamplePrice(BaseModel):
    product: str
    price_pkr: float


class StateSnapshot(BaseModel):
    description: str
    sample_prices: list[SamplePrice]


class FinalReport(BaseModel):
    insight_card: InsightCard
    impact_metrics: ImpactMetricsCard
    actions_taken: list[ActionTaken]
    execution_log: list[ExecutionLogEntry]
    before_state: StateSnapshot
    after_state: StateSnapshot
