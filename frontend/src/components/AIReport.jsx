import React from 'react'
import Badge from './ui/Badge.jsx'
import Button from './ui/Button.jsx'

const TRANSLATIONS = {
  en: {
    reportTitle: 'MandiSense Daily AI Intelligence Report',
    marketRegion: 'Market Region', date: 'Date',
    financials: 'Financial Summary', estRevenue: 'Est. Revenue', estProfit: 'Est. Profit', expectedSales: 'Sales Volume',
    weatherTitle: 'Weather Conditions', temperature: 'Temperature', humidity: 'Humidity', rainfall: 'Rainfall',
    aiInsight: "AI Business Insights",
    recommendationsTable: 'Price Recommendations',
    product: 'Product', mandiPrice: 'Mandi Price', suggestedPrice: 'Suggested', change: 'Δ%', spoilage: 'Risk', suggestion: 'AI Action',
    printBtn: 'Print / Save PDF', closeBtn: 'Close',
  },
  hi: {
    reportTitle: 'मंडीसेंस दैनिक AI रिपोर्ट',
    marketRegion: 'बाज़ार क्षेत्र', date: 'दिनांक',
    financials: 'वित्तीय सारांश', estRevenue: 'अनुमानित राजस्व', estProfit: 'अनुमानित लाभ', expectedSales: 'बिक्री मात्रा',
    weatherTitle: 'मौसम', temperature: 'तापमान', humidity: 'नमी', rainfall: 'वर्षा',
    aiInsight: 'AI व्यापार अंतर्दृष्टि',
    recommendationsTable: 'मूल्य सिफारिशें',
    product: 'उत्पाद', mandiPrice: 'मंडी दर', suggestedPrice: 'सिफारिशित', change: 'Δ%', spoilage: 'जोखिम', suggestion: 'AI क्रिया',
    printBtn: 'प्रिंट / PDF', closeBtn: 'बंद करें',
  },
  ta: {
    reportTitle: 'மண்டிசென்ஸ் தினசரி AI அறிக்கை',
    marketRegion: 'சந்தை பகுதி', date: 'தேதி',
    financials: 'நிதி சுருக்கம்', estRevenue: 'மதிப்பிடப்பட்ட வருவாய்', estProfit: 'மதிப்பிடப்பட்ட லாபம்', expectedSales: 'விற்பனை அளவு',
    weatherTitle: 'வானிலை', temperature: 'வெப்பநிலை', humidity: 'ஈரப்பதம்', rainfall: 'மழை',
    aiInsight: 'AI வணிக நுண்ணறிவுகள்',
    recommendationsTable: 'விலை பரிந்துரைகள்',
    product: 'தயாரிப்பு', mandiPrice: 'மண்டி விலை', suggestedPrice: 'பரிந்துரை', change: 'Δ%', spoilage: 'ஆபத்து', suggestion: 'AI நடவடிக்கை',
    printBtn: 'அச்சிடு / PDF', closeBtn: 'மூடு',
  },
}

export default function AIReport({ show, onClose, regionName, recommendations, weather, summary, language }) {
  const t = TRANSLATIONS[language] || TRANSLATIONS.en
  if (!show) return null

  const recs = recommendations || []
  const totalDemand  = recs.reduce((s, r) => s + (r.demand_forecast?.[0]?.predicted_volume || 0), 0)
  const totalRevenue = recs.reduce((s, r) => s + (r.demand_forecast?.[0]?.predicted_volume || 20) * r.suggested_price, 0)
  const totalProfit  = recs.reduce((s, r) => s + (r.demand_forecast?.[0]?.predicted_volume || 20) * (r.suggested_price - r.current_price), 0)
  const today = new Date().toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })

  return (
    <>
      {/* Backdrop */}
      <div
        onClick={onClose}
        style={{
          position: 'fixed', inset: 0,
          background: 'rgba(11,14,20,0.85)',
          backdropFilter: 'blur(12px)',
          zIndex: 200,
        }}
      />

      {/* Modal */}
      <div style={{
        position: 'fixed', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center',
        zIndex: 201, padding: 'var(--s-4)', overflowY: 'auto',
      }}>
        <div
          onClick={e => e.stopPropagation()}
          style={{
            width: '100%', maxWidth: 720,
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-default)',
            borderRadius: 'var(--r-xl)',
            boxShadow: 'var(--shadow-xl)',
            overflow: 'hidden',
            animation: 'modalIn 0.3s cubic-bezier(0.16,1,0.3,1)',
            margin: 'auto',
          }}
          className="no-print"
        >
          {/* Gradient Header */}
          <div style={{
            background: 'var(--accent-gradient)',
            padding: 'var(--s-5) var(--s-6)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--s-3)' }}>
              <span className="material-symbols-rounded" style={{ fontSize: 28, color: 'white' }}>eco</span>
              <div>
                <div style={{ fontWeight: 800, fontSize: 'var(--text-h3)', color: 'white', letterSpacing: '-0.02em' }}>{t.reportTitle}</div>
                <div style={{ fontSize: 'var(--text-xs)', color: 'rgba(255,255,255,0.7)', marginTop: 2 }}>
                  {t.marketRegion}: <strong style={{ color: 'white' }}>{regionName}</strong> · {t.date}: {today}
                </div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 'var(--s-2)', flexShrink: 0 }}>
              <button
                onClick={() => window.print()}
                style={{ background: 'rgba(255,255,255,0.2)', border: 'none', borderRadius: 'var(--r-md)', padding: 'var(--s-2) var(--s-3)', color: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6, fontSize: 'var(--text-xs)', fontWeight: 700, fontFamily: 'var(--font)' }}
              >
                <span className="material-symbols-rounded" style={{ fontSize: 16 }}>print</span>
                {t.printBtn}
              </button>
              <button
                onClick={onClose}
                style={{ background: 'rgba(255,255,255,0.2)', border: 'none', borderRadius: 'var(--r-md)', width: 32, height: 32, color: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'var(--font)' }}
              >
                <span className="material-symbols-rounded" style={{ fontSize: 18 }}>close</span>
              </button>
            </div>
          </div>

          {/* Body */}
          <div style={{ padding: 'var(--s-6)', display: 'flex', flexDirection: 'column', gap: 'var(--s-5)', maxHeight: '70vh', overflowY: 'auto' }}>

            {/* KPI Row */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--s-4)' }}>
              {[
                { icon: 'trending_up', label: t.estRevenue, val: `₹${totalRevenue.toFixed(0)}`, color: 'var(--success)', bg: 'var(--success-bg)' },
                { icon: 'payments', label: t.estProfit, val: `₹${totalProfit.toFixed(0)}`, color: 'var(--accent-solid)', bg: 'var(--accent-bg)' },
                { icon: 'analytics', label: t.expectedSales, val: `${totalDemand.toFixed(0)} kg`, color: 'var(--info)', bg: 'var(--info-bg)' },
              ].map(kpi => (
                <div key={kpi.label} style={{ background: kpi.bg, borderRadius: 'var(--r-md)', padding: 'var(--s-4)', textAlign: 'center', border: `1px solid ${kpi.color}22` }}>
                  <span className="material-symbols-rounded" style={{ fontSize: 22, color: kpi.color, display: 'block', marginBottom: 4 }}>{kpi.icon}</span>
                  <div style={{ fontWeight: 800, fontSize: '1.1rem', color: kpi.color, letterSpacing: '-0.02em' }}>{kpi.val}</div>
                  <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', marginTop: 2, fontWeight: 600 }}>{kpi.label}</div>
                </div>
              ))}
            </div>

            {/* Weather + AI Summary */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--s-4)' }}>
              {/* Weather */}
              {weather && (
                <div style={{ background: 'var(--bg-elevated)', borderRadius: 'var(--r-md)', padding: 'var(--s-4)', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 'var(--s-3)' }}>
                    <span className="material-symbols-rounded" style={{ fontSize: 14, verticalAlign: 'middle', marginRight: 4, color: 'var(--info)' }}>wb_sunny</span>
                    {t.weatherTitle}
                  </div>
                  {[
                    { label: t.temperature, val: `${weather.temp_max || 32}°C` },
                    { label: t.humidity, val: `${weather.humidity || 60}%` },
                    { label: t.rainfall, val: `${weather.rainfall || 0} mm` },
                  ].map(item => (
                    <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--s-2)', fontSize: 'var(--text-sm)' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>{item.label}</span>
                      <strong>{item.val}</strong>
                    </div>
                  ))}
                </div>
              )}

              {/* AI Summary */}
              {summary && (
                <div style={{ background: 'var(--accent-bg)', borderRadius: 'var(--r-md)', padding: 'var(--s-4)', borderLeft: '3px solid var(--accent-solid)', border: '1px solid var(--border-active)' }}>
                  <div style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: 'var(--accent-solid)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 'var(--s-3)' }}>
                    <span className="material-symbols-rounded" style={{ fontSize: 14, verticalAlign: 'middle', marginRight: 4 }}>auto_awesome</span>
                    {t.aiInsight}
                  </div>
                  <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                    {summary.overall_performance}
                  </p>
                </div>
              )}
            </div>

            {/* Recommendations Table */}
            <div>
              <div style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 'var(--s-3)' }}>
                <span className="material-symbols-rounded" style={{ fontSize: 14, verticalAlign: 'middle', marginRight: 6, color: 'var(--accent-solid)' }}>sell</span>
                {t.recommendationsTable}
              </div>
              <div className="table-container">
                <table className="modern-table" style={{ fontSize: 'var(--text-xs)' }}>
                  <thead>
                    <tr>
                      <th>{t.product}</th>
                      <th>{t.mandiPrice}</th>
                      <th>{t.suggestedPrice}</th>
                      <th>{t.change}</th>
                      <th>{t.spoilage}</th>
                      <th>{t.suggestion}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recs.map(r => {
                      const riskVariant = r.risk_score > 66 ? 'danger' : r.risk_score > 33 ? 'warning' : 'success'
                      const actionVariant = r.action === 'reduce' ? 'danger' : r.action === 'increase' ? 'success' : 'muted'
                      return (
                        <tr key={r.item_id}>
                          <td style={{ fontWeight: 700 }}>{r.item_name}</td>
                          <td>₹{r.current_price}</td>
                          <td style={{ fontWeight: 700, color: 'var(--accent-solid)' }}>₹{r.suggested_price}</td>
                          <td>
                            <Badge variant={actionVariant}>
                              {r.price_change_pct > 0 ? '+' : ''}{r.price_change_pct}%
                            </Badge>
                          </td>
                          <td><Badge variant={riskVariant}>{r.risk_score?.toFixed(0)}%</Badge></td>
                          <td style={{ maxWidth: 140 }}>
                            <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)' }}>
                              {r.explanation?.slice(0, 60)}{r.explanation?.length > 60 ? '…' : ''}
                            </span>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Print-only view (white, for PDF) ── */}
      <style>{`
        @media print {
          .no-print { display: none !important; }
          body { background: white !important; color: #1e293b !important; }
          .print-only { display: block !important; }
        }
      `}</style>
    </>
  )
}
