import { motion } from 'framer-motion';
import { Check, Loader2, Circle, AlertCircle } from 'lucide-react';

const AGENTS = [
  { key: 'news_parser', label: 'News Parser', emoji: '📰' },
  { key: 'impact_analyzer', label: 'Impact Analyzer', emoji: '📊' },
  { key: 'action_generator', label: 'Action Generator', emoji: '⚡' },
  { key: 'executor', label: 'Executor', emoji: '🚀' },
  { key: 'output_composer', label: 'Report Composer', emoji: '📋' },
];

function getAgentStatus(events, agentKey) {
  const started = events.some(e => e.event === 'agent_start' && e.agent === agentKey);
  const completed = events.some(e => e.event === 'agent_complete' && e.agent === agentKey);
  const errored = events.some(e => e.event === 'error');
  if (completed) return 'done';
  if (started) return 'running';
  if (errored) return 'error';
  return 'pending';
}

export default function PipelineProgress({ events = [] }) {
  return (
    <div className="gradient-border p-6 rounded-2xl">
      <h3 className="text-lg font-semibold mb-4">Agent Pipeline</h3>
      <div className="flex items-center justify-between gap-2">
        {AGENTS.map(({ key, label, emoji }, i) => {
          const status = getAgentStatus(events, key);
          return (
            <div key={key} className="flex items-center gap-2 flex-1">
              <motion.div
                initial={{ scale: 0.8 }}
                animate={{ scale: status === 'running' ? [1, 1.15, 1] : 1 }}
                transition={status === 'running' ? { repeat: Infinity, duration: 1.5 } : {}}
                className={`flex flex-col items-center gap-1 p-3 rounded-xl transition-all min-w-[80px] ${
                  status === 'done'
                    ? 'bg-[var(--color-success)]/10 border border-[var(--color-success)]/30'
                    : status === 'running'
                    ? 'bg-[var(--color-accent)]/10 border border-[var(--color-accent)]/30 pulse-glow'
                    : status === 'error'
                    ? 'bg-[var(--color-danger)]/10 border border-[var(--color-danger)]/30'
                    : 'bg-[var(--color-surface-elevated)] border border-[var(--color-border)]'
                }`}
              >
                <span className="text-lg">{emoji}</span>
                <span className="text-[10px] font-medium text-center leading-tight text-[var(--color-text-secondary)]">{label}</span>
                <div className="mt-1">
                  {status === 'done' && <Check className="w-4 h-4 text-[var(--color-success)]" />}
                  {status === 'running' && <Loader2 className="w-4 h-4 text-[var(--color-accent)] animate-spin" />}
                  {status === 'error' && <AlertCircle className="w-4 h-4 text-[var(--color-danger)]" />}
                  {status === 'pending' && <Circle className="w-4 h-4 text-[var(--color-border)]" />}
                </div>
              </motion.div>
              {i < AGENTS.length - 1 && (
                <div className={`h-0.5 flex-1 rounded transition-all ${
                  status === 'done' ? 'bg-[var(--color-success)]' : 'bg-[var(--color-border)]'
                }`} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
