import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { History, ArrowRight } from 'lucide-react';
import { getHistory } from '../api/client';

const severityColors = {
  low: 'bg-green-500/20 text-green-400',
  medium: 'bg-yellow-500/20 text-yellow-400',
  high: 'bg-orange-500/20 text-orange-400',
  critical: 'bg-red-500/20 text-red-400',
};

export default function HistoryPage() {
  const [jobs, setJobs] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    getHistory().then(({ data }) => setJobs(data)).catch(console.error);
  }, []);

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <History className="w-6 h-6 text-[var(--color-accent)]" />
        Analysis History
      </h1>

      {jobs.length === 0 ? (
        <div className="text-center py-16 text-[var(--color-text-secondary)]">
          <History className="w-12 h-12 mx-auto mb-4 opacity-30" />
          <p className="text-lg mb-2">No analyses yet</p>
          <button onClick={() => navigate('/')} className="text-[var(--color-accent)] hover:underline text-sm">Run your first analysis →</button>
        </div>
      ) : (
        <div className="space-y-3">
          {jobs.map((job, i) => (
            <motion.div key={job.job_id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
              onClick={() => navigate(`/results/${job.job_id}`)}
              className="p-4 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)] hover:border-[var(--color-accent)] cursor-pointer transition-all flex items-center justify-between group">
              <div>
                <p className="font-medium">{job.headline || 'Untitled analysis'}</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`px-2 py-0.5 text-[10px] rounded-full ${job.status === 'completed' ? 'bg-[var(--color-success)]/20 text-[var(--color-success)]' : 'bg-[var(--color-warning)]/20 text-[var(--color-warning)]'}`}>{job.status}</span>
                  <span className="text-xs text-[var(--color-text-secondary)]">{job.event_count} events</span>
                </div>
              </div>
              <ArrowRight className="w-5 h-5 text-[var(--color-text-secondary)] group-hover:text-[var(--color-accent)] transition-colors" />
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
