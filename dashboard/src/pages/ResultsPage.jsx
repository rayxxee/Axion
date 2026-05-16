import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useSSE } from '../hooks/useSSE';
import { getResult } from '../api/client';
import PipelineProgress from '../components/PipelineProgress';
import InsightCard from '../components/InsightCard';
import ImpactMetrics from '../components/ImpactMetrics';
import ActionList from '../components/ActionList';
import ExecutionLog from '../components/ExecutionLog';
import BeforeAfterTable from '../components/BeforeAfterTable';
import NotificationPreview from '../components/NotificationPreview';

export default function ResultsPage() {
  const { jobId } = useParams();
  const { events, isComplete, error } = useSSE(jobId);
  const [report, setReport] = useState(null);

  useEffect(() => {
    if (isComplete && jobId) {
      getResult(jobId).then(({ data }) => {
        if (data.report) setReport(data.report);
      }).catch(console.error);
    }
  }, [isComplete, jobId]);

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Analysis Results</h1>

      <PipelineProgress events={events} />

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
              topicBadge={report.insight_card?.topic_badge}
              severityBadge={report.insight_card?.severity_badge}
              credibilityScore={report.insight_card?.credibility_score}
              oneLiner={report.insight_card?.one_liner}
            />
            <ImpactMetrics
              costChangePkr={report.impact_metrics?.cost_change_pkr}
              marginChangePct={report.impact_metrics?.margin_change_pct}
              affectedOrdersCount={report.impact_metrics?.affected_orders_count}
              affectedSectors={report.impact_metrics?.affected_sectors}
              riskLevel={report.impact_metrics?.risk_level}
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ActionList actions={report.actions_taken} />
            <ExecutionLog entries={report.execution_log} />
          </div>

          <BeforeAfterTable
            beforePrices={report.before_state?.sample_prices}
            afterPrices={report.after_state?.sample_prices}
          />

          {report.execution_log && (
            <NotificationPreview
              emailTemplate={null}
              smsTemplate={null}
              pushNotification={null}
            />
          )}
        </>
      )}

      {!report && !error && (
        <div className="text-center py-12 text-[var(--color-text-secondary)]">
          <div className="w-8 h-8 border-2 border-[var(--color-accent)]/30 border-t-[var(--color-accent)] rounded-full animate-spin mx-auto mb-4" />
          <p>Processing pipeline... Watch the agents work above.</p>
        </div>
      )}
    </div>
  );
}
