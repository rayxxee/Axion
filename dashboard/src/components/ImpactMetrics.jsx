import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, DollarSign, Percent, ShoppingCart, AlertTriangle } from 'lucide-react';

export default function ImpactMetrics({ costChangePkr, marginChangePct, affectedOrdersCount, affectedSectors, riskLevel }) {
  const metrics = [
    {
      label: 'Cost Change',
      value: costChangePkr ? `PKR ${(costChangePkr / 1000).toFixed(0)}K` : '—',
      raw: costChangePkr || 0,
      icon: DollarSign,
      positive: costChangePkr < 0,
    },
    {
      label: 'Margin Impact',
      value: marginChangePct ? `${marginChangePct > 0 ? '+' : ''}${marginChangePct?.toFixed(1)}%` : '—',
      raw: marginChangePct || 0,
      icon: Percent,
      positive: marginChangePct > 0,
    },
    {
      label: 'Orders Affected',
      value: affectedOrdersCount?.toString() || '0',
      raw: affectedOrdersCount || 0,
      icon: ShoppingCart,
      positive: false,
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="space-y-4"
    >
      {/* Risk Level Banner */}
      <div className="flex items-center gap-3 p-4 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)]">
        <AlertTriangle className="w-5 h-5 text-[var(--color-warning)]" />
        <span className="text-2xl">{riskLevel}</span>
        <span className="text-sm font-medium text-[var(--color-text-secondary)]">Risk Level</span>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-3 gap-4">
        {metrics.map(({ label, value, raw, icon: Icon, positive }, i) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 + i * 0.1 }}
            className="p-4 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)] hover:border-[var(--color-accent)] transition-all"
          >
            <div className="flex items-center justify-between mb-2">
              <Icon className="w-4 h-4 text-[var(--color-text-secondary)]" />
              {raw !== 0 && (
                positive
                  ? <TrendingUp className="w-4 h-4 text-[var(--color-success)]" />
                  : <TrendingDown className="w-4 h-4 text-[var(--color-danger)]" />
              )}
            </div>
            <p className="text-2xl font-bold">{value}</p>
            <p className="text-xs text-[var(--color-text-secondary)] mt-1">{label}</p>
          </motion.div>
        ))}
      </div>

      {/* Affected Sectors */}
      {affectedSectors?.length > 0 && (
        <div className="flex flex-wrap gap-2">
          <span className="text-xs text-[var(--color-text-secondary)] self-center">Sectors:</span>
          {affectedSectors.map((sector) => (
            <span
              key={sector}
              className="px-3 py-1 text-xs rounded-full bg-[var(--color-surface-elevated)] text-[var(--color-text-primary)] border border-[var(--color-border)]"
            >
              {sector}
            </span>
          ))}
        </div>
      )}
    </motion.div>
  );
}
