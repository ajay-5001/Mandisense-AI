import React from 'react'

/**
 * PageHeader — Consistent page title + subtitle + optional action button.
 * Props:
 *   title    — string
 *   subtitle — string
 *   action   — React node (button etc)
 *   badge    — React node (status badge)
 */
export default function PageHeader({ title, subtitle, action, badge }) {
  return (
    <div className="pg-header">
      <div className="pg-header-left">
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--s-3)', flexWrap: 'wrap' }}>
          <h2 className="pg-title">{title}</h2>
          {badge && badge}
        </div>
        {subtitle && <p className="pg-subtitle">{subtitle}</p>}
      </div>
      {action && <div style={{ flexShrink: 0 }}>{action}</div>}
    </div>
  )
}
