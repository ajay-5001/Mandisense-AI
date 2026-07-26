import React from 'react'

/**
 * Card — The ONE card shell used everywhere.
 * Props:
 *   className  — extra CSS classes
 *   padding    — override padding (default: uses .card CSS)
 *   interactive — adds lift-on-hover
 *   accent     — adds gradient top-border (used for AI summary)
 *   style      — inline style overrides
 */
export default function Card({
  children,
  className = '',
  interactive = false,
  accent = false,
  style,
  ...rest
}) {
  const classes = [
    'card',
    interactive ? 'interactive' : '',
    accent ? 'card-accent' : '',
    className,
  ].filter(Boolean).join(' ')

  return (
    <div className={classes} style={style} {...rest}>
      {children}
    </div>
  )
}

/**
 * Card.Header — optional header area with title + optional right action
 */
Card.Header = function CardHeader({ title, icon, action, children }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: 'var(--s-5)',
    }}>
      <div className="chart-title" style={{ marginBottom: 0 }}>
        {icon && (
          <span className="material-symbols-rounded" style={{ fontSize: 18, color: 'var(--accent-solid)' }}>
            {icon}
          </span>
        )}
        {title}
      </div>
      {action && <div>{action}</div>}
      {children}
    </div>
  )
}
