import { motion } from 'framer-motion';
import { ArrowRight, TrendingUp, TrendingDown } from 'lucide-react';

export default function BeforeAfterTable({ beforePrices = [], afterPrices = [] }) {
  const rows = beforePrices.map((bp, i) => {
    const ap = afterPrices[i] || {};
    const change = bp.price_pkr ? ((ap.price_pkr - bp.price_pkr) / bp.price_pkr * 100) : 0;
    return { product: bp.product, before: bp.price_pkr, after: ap.price_pkr, change };
  });

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="gradient-border p-6 rounded-2xl">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <ArrowRight className="w-5 h-5 text-[var(--color-accent)]" />
        Before / After Pricing
      </h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-[var(--color-text-secondary)] border-b border-[var(--color-border)]">
              <th className="text-left py-3 font-medium">Product</th>
              <th className="text-right py-3 font-medium">Before (PKR)</th>
              <th className="text-right py-3 font-medium">After (PKR)</th>
              <th className="text-right py-3 font-medium">Change</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <motion.tr key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 + i * 0.05 }}
                className="border-b border-[var(--color-border)]/50 hover:bg-[var(--color-surface-elevated)] transition-colors">
                <td className="py-3 font-medium">{row.product}</td>
                <td className="text-right py-3 text-[var(--color-text-secondary)]">{row.before?.toLocaleString()}</td>
                <td className="text-right py-3 font-medium">{row.after?.toLocaleString()}</td>
                <td className={`text-right py-3 font-medium flex items-center justify-end gap-1 ${row.change > 0 ? 'text-[var(--color-danger)]' : 'text-[var(--color-success)]'}`}>
                  {row.change > 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                  {row.change > 0 ? '+' : ''}{row.change.toFixed(1)}%
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}
