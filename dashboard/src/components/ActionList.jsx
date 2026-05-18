import { motion } from 'framer-motion';
import { Check, Clock, Zap } from 'lucide-react';

export default function ActionList({ actions = [] }) {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="gradient-border p-6 rounded-2xl">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Zap className="w-5 h-5 text-[var(--color-accent)]" />
        Recommended Actions
      </h3>
      <div className="space-y-3">
        {actions.map((action, i) => (
          <motion.div key={action.rank || i} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 + i * 0.1 }}
            className="p-4 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)] hover:border-[var(--color-accent)] transition-all">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-[var(--color-accent)]/20 flex items-center justify-center text-[var(--color-accent)] font-bold text-sm shrink-0">{action.rank}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="font-medium text-sm truncate">{action.title}</h4>
                  {action.status === 'simulated' && (
                    <span className="px-2 py-0.5 text-[10px] font-medium rounded-full bg-[var(--color-success)]/20 text-[var(--color-success)] shrink-0">
                      <Check className="w-3 h-3 inline mr-0.5" />Simulated
                    </span>
                  )}
                </div>
                <p className="text-xs text-[var(--color-text-secondary)] mt-1 line-clamp-2">{action.expected_outcome || action.rationale}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
