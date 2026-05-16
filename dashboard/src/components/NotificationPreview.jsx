import { useState } from 'react';
import { motion } from 'framer-motion';
import { Mail, MessageSquare, Bell } from 'lucide-react';

const tabs = [
  { id: 'email', label: 'Email', icon: Mail },
  { id: 'sms', label: 'SMS', icon: MessageSquare },
  { id: 'push', label: 'Push', icon: Bell },
];

export default function NotificationPreview({ emailTemplate, smsTemplate, pushNotification }) {
  const [active, setActive] = useState('email');

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }} className="gradient-border p-6 rounded-2xl">
      <h3 className="text-lg font-semibold mb-4">Notification Previews</h3>
      <div className="flex gap-2 mb-4">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button key={id} onClick={() => setActive(id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${active === id ? 'bg-[var(--color-accent)] text-white' : 'bg-[var(--color-surface-elevated)] text-[var(--color-text-secondary)]'}`}>
            <Icon className="w-3.5 h-3.5" />{label}
          </button>
        ))}
      </div>

      {active === 'email' && emailTemplate && (
        <div className="bg-white rounded-xl p-4 text-gray-900 text-sm">
          <p className="font-bold text-gray-700 mb-2">Subject: {emailTemplate.subject}</p>
          <hr className="mb-2" />
          <div dangerouslySetInnerHTML={{ __html: emailTemplate.body_html }} />
        </div>
      )}

      {active === 'sms' && smsTemplate && (
        <div className="max-w-xs mx-auto">
          <div className="bg-[var(--color-surface-elevated)] rounded-2xl rounded-bl-sm p-4 text-sm">
            <p>{smsTemplate.message}</p>
            <p className="text-xs text-[var(--color-text-secondary)] mt-2 italic">{smsTemplate.urdu_transliteration}</p>
          </div>
        </div>
      )}

      {active === 'push' && pushNotification && (
        <div className="max-w-sm mx-auto bg-[var(--color-surface-elevated)] rounded-xl p-4 border border-[var(--color-border)]">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[var(--color-accent)] to-purple-500 flex items-center justify-center shrink-0">
              <Bell className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="font-semibold text-sm">{pushNotification.title}</p>
              <p className="text-xs text-[var(--color-text-secondary)] mt-0.5">{pushNotification.body}</p>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
}
