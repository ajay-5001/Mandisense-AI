import React from 'react'

/**
 * Button — Unified button component.
 * Props:
 *   variant  — 'primary' | 'ghost' | 'tab' | 'danger'
 *   active   — boolean (for tab variant active state)
 *   size     — 'sm' | 'md' (default md)
 *   icon     — Material Symbol name string
 *   iconPos  — 'left' | 'right' (default left)
 */
export default function Button({
  children,
  variant = 'primary',
  active = false,
  size = 'md',
  icon,
  iconPos = 'left',
  className = '',
  style,
  ...rest
}) {
  const variantClass = {
    primary: 'btn btn-primary',
    ghost:   'btn btn-ghost',
    tab:     `btn btn-tab${active ? ' active' : ''}`,
    danger:  'btn btn-danger',
  }[variant] || 'btn btn-primary'

  const sizeStyle = size === 'sm'
    ? { padding: 'var(--s-1) var(--s-3)', fontSize: 'var(--text-xs)' }
    : {}

  const classes = [variantClass, className].filter(Boolean).join(' ')

  return (
    <button className={classes} style={{ ...sizeStyle, ...style }} {...rest}>
      {icon && iconPos === 'left' && (
        <span className="material-symbols-rounded" style={{ fontSize: size === 'sm' ? 14 : 16 }}>
          {icon}
        </span>
      )}
      {children}
      {icon && iconPos === 'right' && (
        <span className="material-symbols-rounded" style={{ fontSize: size === 'sm' ? 14 : 16 }}>
          {icon}
        </span>
      )}
    </button>
  )
}
