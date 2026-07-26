import React from 'react'

/**
 * Badge — Semantic status pill.
 * Props:
 *   variant — 'success' | 'warning' | 'danger' | 'info' | 'accent' | 'muted'
 *   icon    — optional Material Symbol name
 */
export default function Badge({ children, variant = 'muted', icon, style, className = '' }) {
  const classes = ['badge', `badge-${variant}`, className].filter(Boolean).join(' ')
  return (
    <span className={classes} style={style}>
      {icon && (
        <span className="material-symbols-rounded" style={{ fontSize: 11 }}>{icon}</span>
      )}
      {children}
    </span>
  )
}
