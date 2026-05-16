import { useState } from 'react';
import { motion } from 'framer-motion';
import { FileText, Link, FileUp, Zap, Sparkles } from 'lucide-react';

const tabs = [
  { id: 'text', label: 'Text', icon: FileText },
  { id: 'url', label: 'URL', icon: Link },
  { id: 'pdf', label: 'PDF', icon: FileUp },
];

const demoArticles = [
  { label: 'SBP +200bps', text: 'KARACHI: The State Bank of Pakistan (SBP) has announced an increase in the policy rate by 200 basis points, bringing the key interest rate to 19.5%. The Monetary Policy Committee (MPC) cited persistent inflationary pressures and external sector vulnerabilities as key factors behind the decision. The rate hike is expected to impact borrowing costs across all sectors, particularly affecting working capital requirements for small and medium enterprises.' },
  { label: 'Petrol +18%', text: 'ISLAMABAD: The Oil and Gas Regulatory Authority (OGRA) has notified an increase in petrol prices by Rs 52.36 per liter, effective immediately. The new price of petrol is Rs 350.86 per liter, up from Rs 298.50. High-speed diesel has also been increased by Rs 48.20 per liter. The government attributed the increase to rising international oil prices.' },
];

export default function ArticleInput({ onSubmit, isLoading }) {
  const [activeTab, setActiveTab] = useState('text');
  const [content, setContent] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (content.trim().length < 10) return;
    onSubmit(activeTab, content);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="gradient-border p-6 rounded-2xl"
    >
      <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
        <Sparkles className="w-5 h-5 text-[var(--color-accent)]" />
        Analyze News Article
      </h2>

      {/* Tabs */}
      <div className="flex gap-2 mb-4">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => { setActiveTab(id); setContent(''); }}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === id
                ? 'bg-[var(--color-accent)] text-white'
                : 'bg-[var(--color-surface-elevated)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
            }`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        {activeTab === 'text' && (
          <div className="relative">
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Paste your news article here..."
              rows={8}
              maxLength={50000}
              className="w-full bg-[var(--color-bg)] border border-[var(--color-border)] rounded-xl p-4 text-[var(--color-text-primary)] placeholder-[var(--color-text-secondary)] font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent transition-all"
            />
            <span className="absolute bottom-3 right-3 text-xs text-[var(--color-text-secondary)]">
              {content.length}/50000
            </span>
          </div>
        )}

        {activeTab === 'url' && (
          <input
            type="url"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="https://www.dawn.com/news/..."
            className="w-full bg-[var(--color-bg)] border border-[var(--color-border)] rounded-xl p-4 text-[var(--color-text-primary)] placeholder-[var(--color-text-secondary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition-all"
          />
        )}

        {activeTab === 'pdf' && (
          <div className="border-2 border-dashed border-[var(--color-border)] rounded-xl p-8 text-center">
            <FileUp className="w-10 h-10 text-[var(--color-text-secondary)] mx-auto mb-3" />
            <p className="text-[var(--color-text-secondary)] text-sm">PDF upload coming soon</p>
          </div>
        )}

        {/* Demo chips */}
        {activeTab === 'text' && (
          <div className="flex gap-2 mt-3">
            <span className="text-xs text-[var(--color-text-secondary)] self-center">Demo:</span>
            {demoArticles.map(({ label, text }) => (
              <button
                key={label}
                type="button"
                onClick={() => setContent(text)}
                className="px-3 py-1 bg-[var(--color-surface-elevated)] text-[var(--color-accent)] text-xs rounded-full hover:bg-[var(--color-accent)] hover:text-white transition-all"
              >
                {label}
              </button>
            ))}
          </div>
        )}

        {/* Submit */}
        <motion.button
          type="submit"
          disabled={isLoading || content.trim().length < 10}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="mt-4 w-full py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-[var(--color-accent)] to-purple-500 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all hover:shadow-lg hover:shadow-[var(--color-accent-glow)]"
        >
          {isLoading ? (
            <>
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Zap className="w-5 h-5" />
              Run Analysis Pipeline
            </>
          )}
        </motion.button>
      </form>
    </motion.div>
  );
}
