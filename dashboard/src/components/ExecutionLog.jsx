import { motion } from 'framer-motion';
import { Clock } from 'lucide-react';

const agentIcons = {
  AnalystAgent: '📰',
  ImpactAgent: '📊',
  StrategyAgent: '⚡',
  'ExecutorAgent:PricingUpdater': '🏷️',
  'ExecutorAgent:NotifDrafter': '📨',
  'ExecutorAgent:WorkflowTrigger': '🔔',
  ComposerAgent: '📋',
};

export default function ExecutionLog({ entries = [] }) {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="gradient-border p-6 rounded-2xl">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Clock className="w-5 h-5 text-[var(--color-accent)]" />
        Execution Timeline
      </h3>
      <div className="space-y-0">
        {entries.map((entry, i) => (
          <motion.div key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 + i * 0.08 }} className="flex gap-4 relative">
            <div className="flex flex-col items-center">
              <div className="w-8 h-8 rounded-full bg-[var(--color-surface-elevated)] border border-[var(--color-border)] flex items-center justify-center text-sm">
                {agentIcons[entry.agent] || '🔧'}
              </div>
              {i < entries.length - 1 && <div className="w-0.5 h-full bg-[var(--color-border)] min-h-[24px]" />}
            </div>
            <div className="pb-4">
              <p className="text-sm font-medium">{entry.action}</p>
              <div className="flex items-center gap-2 mt-1">
                <span className={`px-2 py-0.5 text-[10px] rounded-full ${entry.status === 'completed' ? 'bg-[var(--color-success)]/20 text-[var(--color-success)]' : 'bg-[var(--color-accent)]/20 text-[var(--color-accent)]'}`}>{entry.status}</span>
                <span className="text-[10px] text-[var(--color-text-secondary)]">{entry.timestamp?.split('T')[1]?.split('.')[0] || ''}</span>
              </div>
              <p className="text-xs text-[var(--color-text-secondary)] mt-1">{entry.details}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
