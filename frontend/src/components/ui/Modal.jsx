import React, { useEffect, useRef } from 'react'

/**
 * Modal — Dark-themed modal wrapper.
 * Props:
 *   show        — boolean
 *   onClose     — function
 *   title       — string
 *   maxWidth    — CSS width string (default '520px')
 *   fullHeight  — allow scrolling for tall content
 *   noPadding   — remove body padding (for custom layouts)
 */
export default function Modal({ show, onClose, title, children, maxWidth = '520px', noPadding = false }) {
  const overlayRef = useRef(null)

  useEffect(() => {
    if (!show) return
    const onKey = (e) => { if (e.key === 'Escape') onClose?.() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [show, onClose])

  if (!show) return null

  return (
    <div
      className="modal-overlay"
      ref={overlayRef}
      onClick={(e) => { if (e.target === overlayRef.current) onClose?.() }}
    >
      <div className="modal-content" style={{ maxWidth, width: '100%' }}>
        {title && (
          <div className="modal-header">
            <span className="modal-title">{title}</span>
            <button className="modal-close" onClick={onClose} aria-label="Close">
              <span className="material-symbols-rounded" style={{ fontSize: 18 }}>close</span>
            </button>
          </div>
        )}
        <div className={noPadding ? '' : 'modal-body'}>
          {children}
        </div>
      </div>
    </div>
  )
}
