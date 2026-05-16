import { motion } from 'framer-motion';
import { Shield } from 'lucide-react';

const topicColors = {
  monetary_policy: 'bg-blue-500/20 text-blue-400',
  fiscal_policy: 'bg-violet-500/20 text-violet-400',
  energy: 'bg-orange-500/20 text-orange-400',
  trade: 'bg-cyan-500/20 text-cyan-400',
  taxation: 'bg-rose-500/20 text-rose-400',
  commodities: 'bg-amber-500/20 text-amber-400',
  regulation: 'bg-teal-500/20 text-teal-400',
  other: 'bg-gray-500/20 text-gray-400',
};

const severityColors = {
  low: 'bg-green-500/20 text-green-400',
  medium: 'bg-yellow-500/20 text-yellow-400',
  high: 'bg-orange-500/20 text-orange-400',
  critical: 'bg-red-500/20 text-red-400',
};

export default function InsightCard({ headline, topicBadge, severityBadge, credibilityScore, oneLiner }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="gradient-border p-6 rounded-2xl"
    >
      <h3 className="text-xl font-bold mb-3">{headline}</h3>

      <div className="flex flex-wrap gap-2 mb-4">
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${topicColors[topicBadge] || topicColors.other}`}>
          {topicBadge?.replace('_', ' ').toUpperCase()}
        </span>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${severityColors[severityBadge] || severityColors.low}`}>
          {severityBadge?.toUpperCase()}
        </span>
      </div>

      <p className="text-[var(--color-text-secondary)] text-sm mb-4">{oneLiner}</p>

      {/* Credibility Score */}
      <div className="flex items-center gap-3">
        <Shield className="w-4 h-4 text-[var(--color-accent)]" />
        <div className="flex-1">
          <div className="h-2 bg-[var(--color-surface-elevated)] rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${(credibilityScore || 0) * 100}%` }}
              transition={{ duration: 1, delay: 0.3 }}
              className="h-full bg-gradient-to-r from-[var(--color-accent)] to-purple-500 rounded-full"
            />
          </div>
        </div>
        <span className="text-sm font-medium text-[var(--color-text-secondary)]">
          {((credibilityScore || 0) * 100).toFixed(0)}%
        </span>
      </div>
    </motion.div>
  );
}
