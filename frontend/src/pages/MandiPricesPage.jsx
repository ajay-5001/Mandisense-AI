import React, { useState, useRef, useEffect } from 'react'

const AGMARKNET_URL = 'https://agmarknet.gov.in/marketallwholesaleweekanalysis'

export default function MandiPricesPage() {
  const iframeRef = useRef(null)
  const [status, setStatus] = useState('loading') // 'loading' | 'loaded' | 'blocked'

  // Detect X-Frame-Options / CSP block when iframe fires onLoad
  const handleLoad = () => {
    try {
      // If the site allowed embedding, this throws a cross-origin SecurityError
      // (meaning it actually loaded — just can't be read by JS)
      const body = iframeRef.current?.contentDocument?.body?.innerHTML
      // If we get here without throwing, body is readable (same-origin or empty)
      // An empty body means the browser replaced the blocked response with a blank page
      if (!body || body.trim() === '') {
        setStatus('blocked')
      } else {
        setStatus('loaded')
      }
    } catch {
      // SecurityError = cross-origin content DID load inside the iframe
      setStatus('loaded')
    }
  }

  // Fallback safety net: if onLoad never fires within 8s, assume blocked
  useEffect(() => {
    const timer = setTimeout(() => {
      if (status === 'loading') setStatus('blocked')
    }, 8000)
    return () => clearTimeout(timer)
  }, [status])

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      /* sidebar 100vh − header(56px mobile) − padding(48px) − bottom-nav(64px mobile) = fills nicely */
      height: 'calc(100vh - 48px - 64px)',
      minHeight: 480,
      gap: 0,
    }}>

      {/* ── Page Bar ── */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 0 var(--s-4) 0',
        flexShrink: 0,
        flexWrap: 'wrap',
        gap: 'var(--s-3)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--s-3)', minWidth: 0 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 'var(--r-md)',
            background: 'var(--success-bg)',
            border: '1px solid var(--success-border)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexShrink: 0,
          }}>
            <span className="material-symbols-rounded" style={{ fontSize: 20, color: 'var(--success)' }}>
              price_change
            </span>
          </div>
          <div>
            <h2 className="pg-title" style={{ marginBottom: 0 }}>Official Mandi Prices</h2>
            <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginTop: 2 }}>
              Live wholesale prices via Agmarknet · Ministry of Agriculture, Govt. of India
            </p>
          </div>
        </div>

        <a
          href={AGMARKNET_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-ghost"
          style={{ display: 'inline-flex', alignItems: 'center', gap: 'var(--s-2)', fontSize: 'var(--text-xs)', flexShrink: 0 }}
        >
          <span className="material-symbols-rounded" style={{ fontSize: 15 }}>open_in_new</span>
          Open in New Tab
        </a>
      </div>

      {/* ── Content Area ── */}
      <div style={{
        flex: 1,
        position: 'relative',
        borderRadius: 'var(--r-lg)',
        overflow: 'hidden',
        border: '1px solid var(--border-subtle)',
        background: 'var(--bg-surface)',
        boxShadow: 'var(--shadow-md)',
        minHeight: 0,
      }}>

        {/* Loading Spinner (shown while loading) */}
        {status === 'loading' && (
          <div style={{
            position: 'absolute', inset: 0, zIndex: 10,
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            background: 'var(--bg-surface)',
            gap: 'var(--s-4)',
          }}>
            {/* Animated ring */}
            <div style={{ position: 'relative', width: 64, height: 64 }}>
              <svg width="64" height="64" viewBox="0 0 64 64" style={{ position: 'absolute', inset: 0, animation: 'spin 1.2s linear infinite' }}>
                <circle cx="32" cy="32" r="26" fill="none" stroke="var(--border-default)" strokeWidth="4" />
                <circle cx="32" cy="32" r="26" fill="none" stroke="var(--accent-solid)" strokeWidth="4"
                  strokeLinecap="round" strokeDasharray="40 124" strokeDashoffset="0" />
              </svg>
              <span className="material-symbols-rounded" style={{
                position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
                fontSize: 22, color: 'var(--accent-solid)',
              }}>price_change</span>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontWeight: 700, fontSize: 'var(--text-sm)', color: 'var(--text-primary)', marginBottom: 4 }}>
                Loading Agmarknet
              </div>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
                Connecting to official government price database…
              </div>
            </div>
          </div>
        )}

        {/* Fallback Card (shown if blocked) */}
        {status === 'blocked' && (
          <div style={{
            position: 'absolute', inset: 0, zIndex: 10,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: 'var(--bg-surface)',
            padding: 'var(--s-6)',
          }}>
            <div style={{
              maxWidth: 480,
              width: '100%',
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 'var(--s-5)',
              animation: 'modalIn 0.4s ease',
            }}>
              {/* Icon ring */}
              <div style={{
                position: 'relative',
                width: 88, height: 88,
                borderRadius: '50%',
                background: 'var(--accent-bg)',
                border: '2px solid var(--border-active)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <span className="material-symbols-rounded" style={{ fontSize: 40, color: 'var(--accent-solid)' }}>
                  price_change
                </span>
                {/* Badge */}
                <div style={{
                  position: 'absolute', top: -6, right: -6,
                  width: 26, height: 26, borderRadius: '50%',
                  background: 'var(--warning-bg)', border: '2px solid var(--warning-border)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <span className="material-symbols-rounded" style={{ fontSize: 14, color: 'var(--warning)' }}>shield</span>
                </div>
              </div>

              {/* Text */}
              <div>
                <div style={{ fontWeight: 800, fontSize: '1.1rem', color: 'var(--text-primary)', letterSpacing: '-0.02em', marginBottom: 'var(--s-2)' }}>
                  Official Agmarknet Market Prices
                </div>
                <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                  The official Agmarknet website cannot be embedded inside this dashboard because it uses browser
                  security headers (<code style={{ background: 'var(--bg-elevated)', padding: '1px 5px', borderRadius: 3, fontSize: 'var(--text-xs)', color: 'var(--warning)' }}>X-Frame-Options</code>)
                  that prevent embedding in iframes. This is a government-level security policy and cannot be bypassed.
                </p>
              </div>

              {/* Info chips */}
              <div style={{ display: 'flex', gap: 'var(--s-2)', justifyContent: 'center', flexWrap: 'wrap' }}>
                {[
                  { icon: 'verified', label: 'Official Govt. Source', variant: 'success' },
                  { icon: 'lock', label: 'Secure Policy', variant: 'warning' },
                  { icon: 'update', label: 'Updated Weekly', variant: 'info' },
                ].map(chip => (
                  <span key={chip.label} className={`badge badge-${chip.variant}`} style={{ gap: 5 }}>
                    <span className="material-symbols-rounded" style={{ fontSize: 11 }}>{chip.icon}</span>
                    {chip.label}
                  </span>
                ))}
              </div>

              {/* Primary CTA */}
              <a
                href={AGMARKNET_URL}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'inline-flex', alignItems: 'center', gap: 'var(--s-3)',
                  background: 'var(--accent-gradient)',
                  color: 'white',
                  textDecoration: 'none',
                  fontWeight: 700,
                  fontSize: 'var(--text-sm)',
                  fontFamily: 'var(--font)',
                  border: 'none',
                  borderRadius: 'var(--r-md)',
                  padding: 'var(--s-3) var(--s-8)',
                  boxShadow: 'var(--shadow-accent)',
                  cursor: 'pointer',
                  transition: 'all 150ms ease',
                  width: '100%',
                  maxWidth: 320,
                  justifyContent: 'center',
                }}
                onMouseEnter={e => { e.currentTarget.style.opacity = '0.9'; e.currentTarget.style.transform = 'translateY(-2px)' }}
                onMouseLeave={e => { e.currentTarget.style.opacity = '1'; e.currentTarget.style.transform = 'none' }}
              >
                <span className="material-symbols-rounded" style={{ fontSize: 20 }}>open_in_new</span>
                Open Official Website
              </a>

              {/* Secondary info */}
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                Opens <strong style={{ color: 'var(--text-secondary)' }}>agmarknet.gov.in</strong> in a new tab ·
                Ministry of Agriculture & Farmers Welfare · Government of India
              </p>
            </div>
          </div>
        )}

        {/* The actual iframe (always mounted, hidden when blocked) */}
        <iframe
          ref={iframeRef}
          src={AGMARKNET_URL}
          title="Official Agmarknet Mandi Wholesale Prices"
          onLoad={handleLoad}
          style={{
            width: '100%',
            height: '100%',
            border: 'none',
            display: 'block',
            visibility: status === 'loaded' ? 'visible' : 'hidden',
          }}
          sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox"
        />
      </div>

      {/* ── Footer note ── */}
      <p style={{
        textAlign: 'center',
        fontSize: 'var(--text-xs)',
        color: 'var(--text-muted)',
        paddingTop: 'var(--s-3)',
        flexShrink: 0,
      }}>
        Data sourced from{' '}
        <a href="https://agmarknet.gov.in" target="_blank" rel="noopener noreferrer"
          style={{ color: 'var(--accent-solid)', textDecoration: 'none', fontWeight: 600 }}>
          Agmarknet
        </a>
        {' '}· Agricultural Marketing Information Network · DACFW, Govt. of India
      </p>
    </div>
  )
}
