import { NavLink } from 'react-router-dom';
import { BarChart3, History, Zap } from 'lucide-react';
import { motion } from 'framer-motion';

const navItems = [
  { to: '/', icon: Zap, label: 'Analyze' },
  { to: '/history', icon: History, label: 'History' },
];

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-screen w-64 flex flex-col glass z-50">
      {/* Branding */}
      <div className="p-6 border-b border-[var(--color-border)]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[var(--color-accent)] to-purple-500 flex items-center justify-center">
            <BarChart3 className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-[var(--color-text-primary)]">Axion</h1>
            <p className="text-xs text-[var(--color-text-secondary)]">Impact Analyzer</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                isActive
                  ? 'bg-[var(--color-accent)] bg-opacity-20 text-[var(--color-accent)]'
                  : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-elevated)] hover:text-[var(--color-text-primary)]'
              }`
            }
          >
            <Icon className="w-5 h-5" />
            <span className="font-medium">{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-[var(--color-border)]">
        <div className="px-4 py-2 rounded-lg bg-[var(--color-surface-elevated)]">
          <p className="text-xs text-[var(--color-text-secondary)]">🇵🇰 Pakistan Market</p>
          <p className="text-xs text-[var(--color-text-secondary)] mt-1">PKR Currency</p>
        </div>
      </div>
    </aside>
  );
}
