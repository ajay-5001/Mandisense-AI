import React, { useState, useRef, useEffect } from 'react'

/**
 * Dropdown — Replaces native <select> elements.
 * Props:
 *   value      — current value
 *   onChange   — (value) => void
 *   options    — [{ value, label }] or [string]
 *   placeholder— string
 *   width      — CSS width (default '100%')
 */
export default function Dropdown({ value, onChange, options = [], placeholder = 'Select...', width = '100%', style }) {
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  // Normalize options to { value, label }
  const normalizedOptions = options.map(o =>
    typeof o === 'string' ? { value: o, label: o } : o
  )

  const selectedLabel = normalizedOptions.find(o => o.value === value)?.label || placeholder

  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  return (
    <div ref={ref} style={{ position: 'relative', width, ...style }}>
      <button
        type="button"
        onClick={() => setOpen(v => !v)}
        style={{
          width: '100%',
          background: 'var(--bg-elevated)',
          border: `1px solid ${open ? 'var(--accent-solid)' : 'var(--border-default)'}`,
          borderRadius: 'var(--r-md)',
          color: value ? 'var(--text-primary)' : 'var(--text-muted)',
          padding: 'var(--s-2) var(--s-3)',
          fontFamily: 'var(--font)',
          fontSize: 'var(--text-sm)',
          fontWeight: 500,
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 'var(--s-2)',
          boxShadow: open ? '0 0 0 3px var(--accent-bg)' : 'none',
          transition: 'all 150ms ease',
          textAlign: 'left',
        }}
      >
        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {selectedLabel}
        </span>
        <span
          className="material-symbols-rounded"
          style={{
            fontSize: 16,
            color: 'var(--text-muted)',
            transform: open ? 'rotate(180deg)' : 'none',
            transition: 'transform 150ms ease',
            flexShrink: 0,
          }}
        >
          keyboard_arrow_down
        </span>
      </button>

      {open && (
        <div style={{
          position: 'absolute',
          top: 'calc(100% + 4px)',
          left: 0,
          right: 0,
          background: 'var(--bg-elevated)',
          border: '1px solid var(--border-default)',
          borderRadius: 'var(--r-md)',
          boxShadow: 'var(--shadow-lg)',
          zIndex: 300,
          maxHeight: 220,
          overflowY: 'auto',
          padding: 'var(--s-1)',
          animation: 'modalIn 120ms ease',
        }}>
          {normalizedOptions.map(opt => (
            <button
              key={opt.value}
              type="button"
              onClick={() => { onChange(opt.value); setOpen(false) }}
              style={{
                width: '100%',
                background: opt.value === value ? 'var(--accent-bg)' : 'transparent',
                color: opt.value === value ? 'var(--accent-solid)' : 'var(--text-secondary)',
                border: 'none',
                borderRadius: 'var(--r-sm)',
                padding: 'var(--s-2) var(--s-3)',
                fontFamily: 'var(--font)',
                fontSize: 'var(--text-sm)',
                fontWeight: opt.value === value ? 600 : 400,
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 100ms ease',
              }}
              onMouseEnter={e => {
                if (opt.value !== value) {
                  e.currentTarget.style.background = 'var(--bg-overlay)'
                  e.currentTarget.style.color = 'var(--text-primary)'
                }
              }}
              onMouseLeave={e => {
                if (opt.value !== value) {
                  e.currentTarget.style.background = 'transparent'
                  e.currentTarget.style.color = 'var(--text-secondary)'
                }
              }}
            >
              {opt.label}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
