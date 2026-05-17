import { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { pollStatus, getFinalReport } from '../services/api';
import PipelineProgress from '../components/PipelineProgress';
import InsightCard from '../components/InsightCard';
import ImpactMetrics from '../components/ImpactMetrics';
import ActionList from '../components/ActionList';
import ExecutionLog from '../components/ExecutionLog';
import BeforeAfterTable from '../components/BeforeAfterTable';
import NotificationPreview from '../components/NotificationPreview';

export default function ResultsPage() {
  const { jobId } = useParams();
  const [report, setReport] = useState(null);
  const [pipelineStatus, setPipelineStatus] = useState('processing');
  const [error, setError] = useState(null);
  const pollingRef = useRef(false);

  useEffect(() => {
    if (!jobId || pollingRef.current) return;
    pollingRef.current = true;

    // Build synthetic events for PipelineProgress from poll status
    const syntheticEvents = [];

    pollStatus(
      jobId,
      (data) => {
        setPipelineStatus(data.status || 'processing');
      },
      120000 // 2 min timeout
    ).then(async (completed) => {
      if (completed) {
        try {
          const reportData = await getFinalReport();
          setReport(reportData);
        } catch (err) {
          setError('Failed to fetch report');
        }
      } else {
        setError('Pipeline timed out');
      }
    }).catch(() => {
      setError('Connection failed');
    });
  }, [jobId]);

  // Build pipeline events from execution_log in report
  const pipelineEvents = (report?.execution_log || []).flatMap((entry) => {
    const agentMap = {
      AnalystAgent: 'news_parser',
      ImpactAgent: 'impact_analyzer',
      StrategyAgent: 'action_generator',
      'ExecutorAgent:PricingUpdater': 'executor',
      'ExecutorAgent:NotifDrafter': 'executor',
      'ExecutorAgent:WorkflowTrigger': 'executor',
      ComposerAgent: 'output_composer',
    };
    const key = agentMap[entry.agent] || entry.agent;
    return [
      { event: 'agent_start', agent: key },
      { event: 'agent_complete', agent: key },
    ];
  });

  // Transform before/after state for BeforeAfterTable
  const beforePrices = report?.before_state
    ? (Array.isArray(report.before_state) ? report.before_state : Object.values(report.before_state))
        .map((p) => ({ product: p.name || p.id, price_pkr: p.total_price_pkr || p.price_pkr }))
    : [];

  const afterPrices = report?.after_state
    ? (Array.isArray(report.after_state) ? report.after_state : Object.values(report.after_state))
        .map((p) => ({ product: p.name || p.id, price_pkr: p.total_price_pkr || p.price_pkr }))
    : [];

  // Transform notification_draft for NotificationPreview
  const notif = report?.notification_draft;
  const emailTemplate = notif?.email
    ? { subject: notif.email.subject, body_html: notif.email.body?.replace(/\n/g, '<br/>') || '' }
    : null;
  const smsTemplate = notif?.sms
    ? { message: notif.sms.body, urdu_transliteration: '' }
    : null;
  const pushNotification = notif?.internal_alert
    ? { title: 'Internal Alert', body: notif.internal_alert }
    : null;

  // Transform actions for ActionList
  const actions = (report?.actions || []).map((a) => ({
    rank: a.rank,
    title: a.title,
    status: a.simulate ? 'simulated' : 'recommended',
    savings_pkr: 0, // component handles gracefully
    rationale: a.rationale,
    steps: a.steps,
    expected_outcome: a.expected_outcome,
    effort: a.effort,
    impact: a.impact,
    timeframe: a.timeframe,
  }));

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Analysis Results</h1>

      <PipelineProgress events={pipelineEvents} />

      {/* Status Banner */}
      {pipelineStatus !== 'complete' && !error && !report && (
        <div className="text-center py-12 text-[var(--color-text-secondary)]">
          <div className="w-8 h-8 border-2 border-[var(--color-accent)]/30 border-t-[var(--color-accent)] rounded-full animate-spin mx-auto mb-4" />
          <p>Pipeline running... Antigravity agents are processing.</p>
          <p className="text-xs mt-2 opacity-60">Status: {pipelineStatus}</p>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-[var(--color-danger)]/10 border border-[var(--color-danger)]/30 text-[var(--color-danger)]">
          Pipeline Error: {error}
        </div>
      )}

      {report && (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <InsightCard
              headline={report.insight_card?.headline}
              topicBadge={report.insight_card?.topic_badge || report.insight_card?.topic}
              severityBadge={report.insight_card?.severity || report.insight_card?.severity_badge}
              credibilityScore={report.insight_card?.credibility_score || report.insight_card?.source_credibility_score}
              oneLiner={report.insight_card?.one_line_insight || report.insight_card?.one_liner}
            />
            <ImpactMetrics
              costChangePkr={report.impact_metrics?.delivery_cost_change_pkr || report.impact_metrics?.cost_change_pkr}
              marginChangePct={report.impact_metrics?.margin_change_pct}
              affectedOrdersCount={report.impact_metrics?.affected_orders_per_day || report.impact_metrics?.affected_orders_count}
              affectedSectors={report.impact_metrics?.affected_sectors}
              riskLevel={report.insight_card?.severity || report.impact_metrics?.risk_level}
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ActionList actions={actions} />
            <ExecutionLog entries={report.execution_log || []} />
          </div>

          <BeforeAfterTable
            beforePrices={beforePrices}
            afterPrices={afterPrices}
          />

          {notif && (
            <NotificationPreview
              emailTemplate={emailTemplate}
              smsTemplate={smsTemplate}
              pushNotification={pushNotification}
            />
          )}

          {/* State Change Summary */}
          {report.state_change_summary && (
            <div className="p-4 rounded-xl bg-[var(--color-success)]/10 border border-[var(--color-success)]/30 text-[var(--color-success)] text-sm font-medium">
              ✓ {report.state_change_summary}
            </div>
          )}
        </>
      )}
    </div>
  );
}
