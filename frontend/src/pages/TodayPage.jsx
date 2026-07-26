import React, { useState, useEffect } from 'react'
import AIReport from '../components/AIReport.jsx'
import Badge from '../components/ui/Badge.jsx'
import Button from '../components/ui/Button.jsx'
import Dropdown from '../components/ui/Dropdown.jsx'
import Modal from '../components/ui/Modal.jsx'

const FILTER_OPTIONS = [
  { id: 'all',      labelKey: 'all',      icon: 'apps' },
  { id: 'reduce',   labelKey: 'reduce',   icon: 'south' },
  { id: 'hold',     labelKey: 'hold',     icon: 'remove' },
  { id: 'increase', labelKey: 'increase', icon: 'north' },
]

const TRANSLATIONS = {
  en: {
    greeting: 'Good morning', greetingSub: 'Your daily pricing intelligence overview',
    weatherCard: 'Weather', profitToday: 'Est. Profit', expectedDemand: 'Forecast Demand',
    revenue: 'Projected Revenue', aiScore: 'AI Health Score',
    summaryTitle: "Today's AI Business Summary", notificationsTitle: 'Smart Alerts',
    recsTitle: 'Price Recommendations', searchPlaceholder: 'Search products…',
    all: 'All', reduce: 'Reduce', hold: 'Hold', increase: 'Increase',
    viewDetails: 'View Details', downloadReport: 'Generate Report',
    loadingSummary: 'Analyzing market data…',
    spoilageAlert: 'Critical spoilage risk', discountAlert: 'Discount recommendation',
    weatherAlert: 'Weather disruption signal', restockAlert: 'Restock suggestion',
    noRecs: 'No items match your filters.', close: 'Close',
    perKg: 'per kg', currentStock: 'Current Stock', spoilageRisk: 'Spoilage Risk',
    plannerTitle: "Tomorrow's Purchase Planner",
    plannerSub: 'Enter planned restock. AI flags over/understock risks.',
    savePlan: 'Save Plan', comparatorTitle: 'India-Wide Price Comparator',
    comparatorSub: 'Cheapest sourcing hub across all states.',
    aiRecommended: 'AI Recommended Source', product: 'Product',
    overstock: 'Overstock Risk', understock: 'Understock Risk', optimal: 'Optimal Plan',
    suggestRestock: 'Suggested Restock',
  },
  hi: {
    greeting: 'नमस्ते', greetingSub: 'आज का मूल्य खुफिया अवलोकन',
    weatherCard: 'मौसम', profitToday: 'अनुमानित लाभ', expectedDemand: 'पूर्वानुमान मांग',
    revenue: 'अनुमानित राजस्व', aiScore: 'AI स्वास्थ्य स्कोर',
    summaryTitle: 'आज का AI व्यापार सारांश', notificationsTitle: 'स्मार्ट अलर्ट',
    recsTitle: 'मूल्य सिफारिशें', searchPlaceholder: 'उत्पाद खोजें…',
    all: 'सभी', reduce: 'कम करें', hold: 'स्थिर रखें', increase: 'बढ़ाएं',
    viewDetails: 'विवरण देखें', downloadReport: 'रिपोर्ट जनरेट करें',
    loadingSummary: 'बाजार डेटा का विश्लेषण…',
    spoilageAlert: 'गंभीर खराबी जोखिम', discountAlert: 'छूट की सिफारिश',
    weatherAlert: 'मौसम व्यवधान', restockAlert: 'स्टॉक सुझाव',
    noRecs: 'कोई उत्पाद नहीं मिला।', close: 'बंद करें',
    perKg: 'प्रति किग्रा', currentStock: 'वर्तमान स्टॉक', spoilageRisk: 'खराबी जोखिम',
    plannerTitle: 'कल की खरीद योजना', plannerSub: 'AI स्टॉक जोखिम की जांच करेगा।',
    savePlan: 'योजना सहेजें', comparatorTitle: 'भारत-व्यापी मूल्य तुलना',
    comparatorSub: 'सभी राज्यों में सबसे सस्ता स्रोत।',
    aiRecommended: 'AI अनुशंसित स्रोत', product: 'उत्पाद',
    overstock: 'अधिक स्टॉक जोखिम', understock: 'कम स्टॉक जोखिम', optimal: 'अनुकूल योजना',
    suggestRestock: 'पुनःस्टॉक सुझाव',
  },
  ta: {
    greeting: 'காலை வணக்கம்', greetingSub: 'இன்றைய விலை நுண்ணறிவு சுருக்கம்',
    weatherCard: 'வானிலை', profitToday: 'மதிப்பிடப்பட்ட லாபம்', expectedDemand: 'தேவை கணிப்பு',
    revenue: 'மதிப்பிடப்பட்ட வருவாய்', aiScore: 'AI ஆரோக்கிய குறியீடு',
    summaryTitle: 'இன்றைய AI வணிக சுருக்கம்', notificationsTitle: 'ஸ்மார்ட் அறிவிப்புகள்',
    recsTitle: 'விலை பரிந்துரைகள்', searchPlaceholder: 'தயாரிப்புகளைத் தேடு…',
    all: 'அனைத்தும்', reduce: 'குறைக்க', hold: 'தக்கவைக்க', increase: 'உயர்த்த',
    viewDetails: 'நுண்ணறிவுகளைக் காண்க', downloadReport: 'அறிக்கையை உருவாக்கு',
    loadingSummary: 'சந்தை தரவை பகுப்பாய்கிறது…',
    spoilageAlert: 'கெட்டுப்போகும் ஆபத்து', discountAlert: 'தள்ளுபடி பரிந்துரை',
    weatherAlert: 'வானிலை இடையூறு', restockAlert: 'சரக்கு பரிந்துரை',
    noRecs: 'வடிகட்டிகளுடன் பொருந்தும் பொருட்கள் இல்லை.', close: 'மூடு',
    perKg: 'கிலோவுக்கு', currentStock: 'தற்போதைய இருப்பு', spoilageRisk: 'கெட்டுப்போகும் ஆபத்து',
    plannerTitle: 'நாளைய கொள்முதல் திட்டம்', plannerSub: 'AI சரக்கு ஆபத்துகளை கண்டறியும்.',
    savePlan: 'திட்டத்தை சேமி', comparatorTitle: 'இந்தியா-அளவிலான விலை ஒப்பீடு',
    comparatorSub: 'அனைத்து மாநிலங்களிலும் மலிவான மூலம்.',
    aiRecommended: 'AI பரிந்துரைத்த மூலம்', product: 'தயாரிப்பு',
    overstock: 'அதிக இருப்பு ஆபத்து', understock: 'குறைந்த இருப்பு ஆபத்து', optimal: 'சிறந்த திட்டம்',
    suggestRestock: 'மீண்டும் சேமிக்க பரிந்துரை',
  },
}

// ── Tooltip component for Recharts ──
function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: 'var(--bg-elevated)',
      border: '1px solid var(--border-default)',
      borderRadius: 'var(--r-md)',
      padding: '8px 12px',
      boxShadow: 'var(--shadow-lg)',
    }}>
      <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', fontWeight: 700, marginBottom: 4 }}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: p.color, fontSize: 'var(--text-xs)', display: 'flex', gap: 8, justifyContent: 'space-between', minWidth: 120 }}>
          <span>{p.name}:</span>
          <span style={{ fontWeight: 700 }}>{typeof p.value === 'number' ? p.value.toFixed(1) : p.value}</span>
        </div>
      ))}
    </div>
  )
}

export default function TodayPage({ regionId, language }) {
  const [recommendations, setRecommendations] = useState(null)
  const [summaryData, setSummaryData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [loadingSummary, setLoadingSummary] = useState(true)
  const [error, setError] = useState(null)
  const [activeFilter, setActiveFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedRecDetails, setSelectedRecDetails] = useState(null)
  const [showReport, setShowReport] = useState(false)
  const [purchasePlans, setPurchasePlans] = useState({})
  const [comparisonProduct, setComparisonProduct] = useState('')
  const [comparisonData, setComparisonData] = useState(null)
  const [loadingCompare, setLoadingCompare] = useState(false)
  const [saveStatus, setSaveStatus] = useState('')

  const t = TRANSLATIONS[language] || TRANSLATIONS.en

  // Determine greeting from time
  const getGreeting = () => {
    const h = new Date().getHours()
    if (h < 12) return `${t.greeting}, Vendor! 🌅`
    if (h < 17) return `Good Afternoon, Vendor! ☀️`
    return `Good Evening, Vendor! 🌙`
  }

  // Load purchase plans
  useEffect(() => {
    fetch('/api/purchase-plans')
      .then(r => r.json())
      .then(data => {
        const m = {}
        if (Array.isArray(data)) data.forEach(p => { m[p.product_name.toLowerCase()] = p.planned_qty })
        setPurchasePlans(m)
      })
      .catch(() => {})
  }, [])

  // Load recommendations
  useEffect(() => {
    setLoading(true)
    setError(null)
    const apiKey = localStorage.getItem('gemini_api_key') || ''
    fetch(`/api/recommend/all/${regionId}?lang=${language}`, {
      headers: apiKey ? { 'X-Gemini-Key': apiKey } : {},
    })
      .then(r => { if (!r.ok) throw new Error('Server error'); return r.json() })
      .then(d => { setRecommendations(d.recommendations); setLoading(false) })
      .catch(e => { setError(e.message); setLoading(false) })
  }, [regionId, language])

  // Load AI summary
  useEffect(() => {
    setLoadingSummary(true)
    const apiKey = localStorage.getItem('gemini_api_key') || ''
    fetch(`/api/ai-summary/${regionId}?lang=${language}`, {
      headers: apiKey ? { 'X-Gemini-Key': apiKey } : {},
    })
      .then(r => r.json())
      .then(d => { setSummaryData(d); setLoadingSummary(false) })
      .catch(() => setLoadingSummary(false))
  }, [regionId, language])

  // Load comparison
  useEffect(() => {
    if (!comparisonProduct) return
    setLoadingCompare(true)
    fetch(`/api/compare/${encodeURIComponent(comparisonProduct)}`)
      .then(r => r.json())
      .then(d => { setComparisonData(d); setLoadingCompare(false) })
      .catch(() => setLoadingCompare(false))
  }, [comparisonProduct])

  // Set default comparison product
  useEffect(() => {
    if (!comparisonProduct && recommendations?.length > 0) {
      setComparisonProduct(recommendations[0].item_name)
    }
  }, [recommendations])

  const handleSavePlans = () => {
    setSaveStatus('Saving…')
    const payload = (recommendations || []).map(r => ({
      product_name: r.item_name,
      planned_qty: parseFloat(purchasePlans[r.item_name.toLowerCase()] || 0),
    }))
    fetch('/api/purchase-plans', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
      .then(r => { if (!r.ok) throw new Error('Failed'); return r.json() })
      .then(() => { setSaveStatus('Saved!'); setTimeout(() => setSaveStatus(''), 2000) })
      .catch(() => setSaveStatus('Error'))
  }

  // ── Loading ──
  if (loading) {
    return (
      <div className="page-content">
        {/* Header skeleton */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--s-6)' }}>
          <div>
            <div className="skeleton-line" style={{ width: 220, height: 26, marginBottom: 8 }} />
            <div className="skeleton-line" style={{ width: 160, height: 14 }} />
          </div>
          <div className="skeleton-card" style={{ width: 160, height: 36 }} />
        </div>
        <div className="kpi-grid">
          {[1, 2, 3, 4].map(i => <div key={i} className="skeleton-card" style={{ height: 100 }} />)}
        </div>
        <div className="skeleton-card" style={{ height: 120, marginBottom: 'var(--s-4)' }} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--s-3)' }}>
          {[1, 2, 3].map(i => <div key={i} className="skeleton-card" style={{ height: 80 }} />)}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-content">
        <div className="glass-card" style={{ textAlign: 'center', padding: 'var(--s-10)' }}>
          <span className="material-symbols-rounded" style={{ fontSize: 48, color: 'var(--danger)' }}>wifi_off</span>
          <h3 style={{ marginTop: 'var(--s-4)', fontSize: 'var(--text-h2)', fontWeight: 700 }}>Dashboard sync failed</h3>
          <p style={{ color: 'var(--text-secondary)', margin: 'var(--s-2) 0 var(--s-5)', fontSize: 'var(--text-sm)' }}>{error}</p>
          <Button variant="primary" icon="refresh" onClick={() => window.location.reload()}>Retry</Button>
        </div>
      </div>
    )
  }

  const recs = recommendations || []
  const lowCount  = recs.filter(r => r.risk_level?.level === 'low').length
  const modCount  = recs.filter(r => r.risk_level?.level === 'moderate').length
  const highCount = recs.filter(r => r.risk_level?.level === 'high').length
  const aiHealthScore = Math.max(20, 100 - (highCount * 12) - (modCount * 4))

  const totalForecastDemand = recs.reduce((acc, r) => acc + (r.demand_forecast?.[0]?.predicted_volume || 0), 0)
  let estimatedRevenue = 0, estimatedProfit = 0
  recs.forEach(r => {
    const dem = r.demand_forecast?.[0]?.predicted_volume || 20
    estimatedRevenue += dem * r.suggested_price
    estimatedProfit  += dem * (r.suggested_price - r.current_price)
  })

  const filteredRecs = recs.filter(rec => {
    const matchFilter = activeFilter === 'all' || rec.action === activeFilter
    const matchSearch = !searchQuery || rec.item_name.toLowerCase().includes(searchQuery.toLowerCase())
    return matchFilter && matchSearch
  })

  const getNotifications = () => {
    const alerts = []
    const highRisk = recs.find(r => r.risk_score > 66)
    if (highRisk) alerts.push({ id: 'spoilage', type: 'danger', title: t.spoilageAlert, desc: `${highRisk.item_name} — risk score ${highRisk.risk_score.toFixed(0)}/100. Lower price to sell quickly.`, icon: 'error' })
    const humidity = summaryData?.raw_data?.weather?.humidity || 50
    if (humidity > 80) alerts.push({ id: 'weather', type: 'warning', title: t.weatherAlert, desc: `High humidity (${humidity}%) detected. Store in a dry area.`, icon: 'rainy' })
    const lowStock = recs.find(r => r.stock_kg < (r.demand_forecast?.[0]?.predicted_volume || 20) * 1.5)
    if (lowStock) alerts.push({ id: 'stock', type: 'info', title: t.restockAlert, desc: `${lowStock.item_name} stock (${lowStock.stock_kg} kg) is low vs. forecast.`, icon: 'shopping_basket' })
    const discount = recs.find(r => r.price_change_pct < -5)
    if (discount) alerts.push({ id: 'discount', type: 'warning', title: t.discountAlert, desc: `Oversupply for ${discount.item_name}. Recommended discount: ${discount.price_change_pct}%.`, icon: 'percent' })
    return alerts.slice(0, 3)
  }

  const today = new Date().toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'short', day: 'numeric' })

  return (
    <div className="page-content">

      {/* ── Page Header ── */}
      <div className="pg-header">
        <div className="pg-header-left">
          <h2 className="pg-title">{getGreeting()}</h2>
          <p className="pg-subtitle">{t.greetingSub} · {today}</p>
        </div>
        <Button
          variant="primary"
          icon="picture_as_pdf"
          onClick={() => setShowReport(true)}
        >
          {t.downloadReport}
        </Button>
      </div>

      {/* ── KPI Grid (4 cards) ── */}
      <div className="kpi-grid">

        {/* Weather */}
        <div className="kpi-card">
          <div className="kpi-header">
            <span>{t.weatherCard}</span>
            <div className="kpi-icon-wrap" style={{ background: 'var(--info-bg)', color: 'var(--info)' }}>
              <span className="material-symbols-rounded" style={{ fontSize: 16 }}>wb_sunny</span>
            </div>
          </div>
          <div className="kpi-value">{summaryData?.raw_data?.weather?.temp_max || 32}°C</div>
          <div className="kpi-sub">Humidity: {summaryData?.raw_data?.weather?.humidity || 60}%</div>
        </div>

        {/* Demand */}
        <div className="kpi-card">
          <div className="kpi-header">
            <span>{t.expectedDemand}</span>
            <div className="kpi-icon-wrap" style={{ background: 'var(--accent-bg)', color: 'var(--accent-solid)' }}>
              <span className="material-symbols-rounded" style={{ fontSize: 16 }}>analytics</span>
            </div>
          </div>
          <div className="kpi-value">{totalForecastDemand.toFixed(0)} kg</div>
          <div className="kpi-sub">Across {recs.length} products</div>
        </div>

        {/* Profit */}
        <div className="kpi-card">
          <div className="kpi-header">
            <span>{t.profitToday}</span>
            <div className="kpi-icon-wrap" style={{ background: 'var(--success-bg)', color: 'var(--success)' }}>
              <span className="material-symbols-rounded" style={{ fontSize: 16 }}>trending_up</span>
            </div>
          </div>
          <div className="kpi-value" style={{ color: 'var(--success)' }}>₹{estimatedProfit.toFixed(0)}</div>
          <div className="kpi-sub">Rev: ₹{estimatedRevenue.toFixed(0)}</div>
        </div>

        {/* AI Score */}
        <div className="kpi-card">
          <div className="kpi-header">
            <span>{t.aiScore}</span>
            <div className="kpi-icon-wrap" style={{ background: 'var(--warning-bg)', color: 'var(--warning)' }}>
              <span className="material-symbols-rounded" style={{ fontSize: 16 }}>shield_with_heart</span>
            </div>
          </div>
          <div className="kpi-value" style={{ color: aiHealthScore > 75 ? 'var(--success)' : 'var(--warning)' }}>
            {aiHealthScore}<span style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-muted)' }}>/100</span>
          </div>
          <Badge variant={aiHealthScore > 75 ? 'success' : 'warning'} icon="verified">
            {aiHealthScore > 75 ? 'Optimized' : 'Monitor'}
          </Badge>
        </div>
      </div>

      {/* ── AI Business Summary ── */}
      {loadingSummary ? (
        <div className="skeleton-card" style={{ height: 130, marginBottom: 'var(--s-6)' }} />
      ) : (
        <div className="ai-summary-card">
          <div className="ai-summary-title">
            <span className="material-symbols-rounded ai-summary-sparkle">auto_awesome</span>
            {t.summaryTitle}
            {summaryData?.gemini_active && (
              <Badge variant="accent" icon="bolt" style={{ marginLeft: 'auto' }}>Gemini Active</Badge>
            )}
          </div>
          <div style={{ display: 'grid', gap: 'var(--s-4)' }} className="dashboard-grid">
            <p style={{ fontSize: 'var(--text-sm)', lineHeight: 1.7, color: 'var(--text-primary)' }}>
              {summaryData?.summary?.overall_performance}
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--s-2)', borderLeft: '2px solid var(--border-default)', paddingLeft: 'var(--s-4)' }}>
              {[
                { icon: 'cloud', label: 'Weather Impact', val: summaryData?.summary?.weather_impact },
                { icon: 'sell', label: 'Discounting', val: summaryData?.summary?.suggested_discounts },
                { icon: 'inventory', label: 'Stock Alerts', val: summaryData?.summary?.stock_warnings },
              ].map(item => (
                <div key={item.label} style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', display: 'flex', gap: 'var(--s-2)' }}>
                  <span className="material-symbols-rounded" style={{ fontSize: 14, color: 'var(--accent-solid)', flexShrink: 0, marginTop: 1 }}>{item.icon}</span>
                  <span><strong style={{ color: 'var(--text-primary)' }}>{item.label}:</strong> {item.val}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Recommendations + Alerts Row ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 'var(--s-4)' }} className="dashboard-grid">

        {/* Recommendations Column */}
        <div style={{ gridColumn: 'span 2' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--s-4)', flexWrap: 'wrap', gap: 'var(--s-2)' }}>
            <h3 style={{ fontSize: 'var(--text-h2)', fontWeight: 700 }}>{t.recsTitle}</h3>
          </div>

          {/* Search */}
          <div className="search-container">
            <span className="material-symbols-rounded">search</span>
            <input
              type="text"
              className="search-field"
              placeholder={t.searchPlaceholder}
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', display: 'flex' }}
              >
                <span className="material-symbols-rounded" style={{ fontSize: 18 }}>close</span>
              </button>
            )}
          </div>

          {/* Filter tabs */}
          <div style={{ display: 'flex', gap: 'var(--s-2)', flexWrap: 'wrap', marginBottom: 'var(--s-4)' }}>
            {FILTER_OPTIONS.map(opt => (
              <Button
                key={opt.id}
                variant="tab"
                active={activeFilter === opt.id}
                icon={opt.icon}
                onClick={() => setActiveFilter(opt.id)}
                size="sm"
              >
                {t[opt.labelKey]}
                {opt.id !== 'all' && (
                  <span style={{
                    fontSize: '0.65rem', fontWeight: 700, marginLeft: 2,
                    background: activeFilter === opt.id ? 'rgba(255,255,255,0.25)' : 'var(--bg-elevated)',
                    padding: '1px 6px', borderRadius: 'var(--r-full)',
                    color: activeFilter === opt.id ? 'white' : 'var(--text-muted)',
                  }}>
                    {recs.filter(r => r.action === opt.id).length}
                  </span>
                )}
              </Button>
            ))}
          </div>

          {/* Rec cards */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--s-3)' }}>
            {filteredRecs.length === 0 ? (
              <div className="glass-card" style={{ textAlign: 'center', padding: 'var(--s-8)' }}>
                <span className="material-symbols-rounded" style={{ fontSize: 40, color: 'var(--text-muted)' }}>search_off</span>
                <p style={{ color: 'var(--text-secondary)', marginTop: 'var(--s-3)', fontSize: 'var(--text-sm)' }}>{t.noRecs}</p>
              </div>
            ) : filteredRecs.map(rec => {
              const isHigh = rec.risk_score > 66
              const isMod  = rec.risk_score > 33
              const level  = isHigh ? 'high' : isMod ? 'moderate' : 'low'
              const actionVariant = rec.action === 'reduce' ? 'danger' : rec.action === 'increase' ? 'success' : 'info'

              return (
                <div
                  key={rec.item_id}
                  className={`glass-card rec-card-premium risk-${level}`}
                  style={{ padding: 'var(--s-5)', cursor: 'default' }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 'var(--s-3)' }}>
                    {/* Left: name + price */}
                    <div style={{ minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--s-2)', flexWrap: 'wrap' }}>
                        <span style={{ fontWeight: 700, fontSize: 'var(--text-h3)' }}>{rec.item_name}</span>
                        <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>{t.perKg}</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'baseline', gap: 'var(--s-2)', marginTop: 'var(--s-2)' }}>
                        <span style={{ fontSize: '1.5rem', fontWeight: 800, letterSpacing: '-0.03em', color: 'var(--text-primary)' }}>
                          ₹{rec.suggested_price}
                        </span>
                        {rec.action !== 'hold' && (
                          <span style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)', textDecoration: 'line-through' }}>
                            ₹{rec.current_price}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Right: badges */}
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 'var(--s-2)', flexShrink: 0 }}>
                      <Badge
                        variant={actionVariant}
                        icon={rec.action === 'reduce' ? 'south' : rec.action === 'increase' ? 'north' : 'remove'}
                      >
                        {rec.price_change_pct > 0 ? '+' : ''}{rec.price_change_pct}%
                      </Badge>
                      <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', fontWeight: 600 }}>
                        {t.spoilageRisk}: {rec.risk_score?.toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  {/* Risk bar */}
                  <div className="risk-bar-track" style={{ margin: 'var(--s-3) 0' }}>
                    <div className={`risk-bar-fill risk-fill-${level}`} style={{ width: `${rec.risk_score}%` }} />
                  </div>

                  {/* Explanation + view details */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 'var(--s-3)' }}>
                    <p style={{
                      fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', flex: 1,
                      overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box',
                      WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', lineHeight: 1.5,
                    }}>
                      {rec.explanation}
                    </p>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={async () => {
                        const apiKey = localStorage.getItem('gemini_api_key') || ''
                        try {
                          const res = await fetch(`/api/recommend/${rec.item_id}/${regionId}?lang=${language}`, {
                            headers: apiKey ? { 'X-Gemini-Key': apiKey } : {},
                          })
                          setSelectedRecDetails(await res.json())
                        } catch { setSelectedRecDetails(rec) }
                      }}
                    >
                      {t.viewDetails}
                    </Button>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Alerts Column */}
        <div>
          <h3 style={{ fontSize: 'var(--text-h2)', fontWeight: 700, marginBottom: 'var(--s-4)' }}>
            {t.notificationsTitle}
          </h3>
          <div className="notification-container">
            {getNotifications().map(notif => (
              <div key={notif.id} className={`notif-card notif-${notif.type}`}>
                <span className="material-symbols-rounded notif-icon">{notif.icon}</span>
                <div className="notif-content">
                  <div className="notif-title">{notif.title}</div>
                  <div className="notif-desc">{notif.desc}</div>
                </div>
              </div>
            ))}
            {getNotifications().length === 0 && (
              <div className="notif-card" style={{ justifyContent: 'center', padding: 'var(--s-6)' }}>
                <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: 'var(--text-sm)' }}>
                  <span className="material-symbols-rounded" style={{ fontSize: 32, display: 'block', marginBottom: 'var(--s-2)' }}>check_circle</span>
                  All clear — no alerts today
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── Purchase Planner + Mandi Comparator ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: 'var(--s-6)', marginTop: 'var(--s-8)' }}>

        {/* Purchase Planner */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--s-4)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 'var(--s-3)' }}>
            <div>
              <h3 style={{ fontSize: 'var(--text-h3)', fontWeight: 700 }}>{t.plannerTitle}</h3>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginTop: 2 }}>{t.plannerSub}</p>
            </div>
            <Button variant="ghost" size="sm" icon="save" onClick={handleSavePlans}>{t.savePlan}</Button>
          </div>

          {saveStatus && (
            <div style={{ padding: 'var(--s-2) var(--s-3)', background: 'var(--info-bg)', color: 'var(--info)', borderRadius: 'var(--r-md)', fontSize: 'var(--text-xs)', fontWeight: 700, textAlign: 'center', border: '1px solid var(--info-border)' }}>
              {saveStatus}
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--s-2)', maxHeight: 340, overflowY: 'auto', paddingRight: 2 }}>
            {(recommendations || []).map(r => {
              const nameLower = r.item_name.toLowerCase()
              const plannedVal = purchasePlans[nameLower] || ''
              const expectedVal = r.demand_forecast?.[0]?.predicted_volume || 15
              const idealVal = Math.max(5, parseFloat((expectedVal * 3 - (r.stock_kg || 0)).toFixed(1)))
              let alertText = `${t.suggestRestock}: ${idealVal} kg`
              let alertVariant = 'info'
              if (plannedVal) {
                const pv = parseFloat(plannedVal)
                if (pv > idealVal * 1.3) { alertText = `${t.overstock}: buying ${pv} vs suggest ${idealVal}`; alertVariant = 'danger' }
                else if (pv < idealVal * 0.7) { alertText = `${t.understock}: buying ${pv} vs suggest ${idealVal}`; alertVariant = 'warning' }
                else { alertText = t.optimal; alertVariant = 'success' }
              }
              return (
                <div key={r.item_id} style={{ padding: 'var(--s-3)', borderRadius: 'var(--r-md)', background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)', display: 'flex', flexDirection: 'column', gap: 'var(--s-2)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--s-2)' }}>
                      <span style={{ fontWeight: 700, fontSize: 'var(--text-sm)' }}>{r.item_name}</span>
                      <Badge variant="info" style={{ fontSize: '0.6rem', padding: '1px 6px' }}>Stock: {r.stock_kg || 0}kg</Badge>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--s-2)' }}>
                      <input
                        type="number"
                        placeholder={idealVal}
                        className="modern-input"
                        style={{ width: 72, padding: 'var(--s-1) var(--s-2)', fontSize: 'var(--text-sm)', textAlign: 'right' }}
                        value={plannedVal}
                        onChange={e => setPurchasePlans({ ...purchasePlans, [nameLower]: e.target.value })}
                      />
                      <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>kg</span>
                    </div>
                  </div>
                  <Badge variant={alertVariant} style={{ alignSelf: 'flex-start', fontSize: '0.6rem' }}>{alertText}</Badge>
                </div>
              )
            })}
          </div>
        </div>

        {/* Mandi Comparator */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--s-4)' }}>
          <div>
            <h3 style={{ fontSize: 'var(--text-h3)', fontWeight: 700 }}>{t.comparatorTitle}</h3>
            <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginTop: 2 }}>{t.comparatorSub}</p>
          </div>

          <div style={{ display: 'flex', gap: 'var(--s-3)', alignItems: 'center' }}>
            <span className="form-label" style={{ whiteSpace: 'nowrap', marginBottom: 0 }}>{t.product}:</span>
            <Dropdown
              value={comparisonProduct}
              onChange={setComparisonProduct}
              options={(recommendations || []).map(r => ({ value: r.item_name, label: r.item_name }))}
            />
          </div>

          {loadingCompare ? (
            <div className="skeleton-card" style={{ height: 240, flex: 1 }} />
          ) : comparisonData?.recommended_mandi ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--s-3)', flex: 1 }}>
              {/* Best mandi highlight */}
              <div style={{ padding: 'var(--s-4)', background: 'var(--accent-bg)', border: '1px solid var(--border-active)', borderRadius: 'var(--r-md)' }}>
                <div style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--accent-solid)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 'var(--s-2)' }}>
                  {t.aiRecommended}
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: 'var(--text-sm)' }}>{comparisonData.recommended_mandi?.mandi_name}</div>
                    <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>{comparisonData.recommended_mandi?.state}</div>
                  </div>
                  <span style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--success)' }}>
                    ₹{comparisonData.recommended_mandi?.wholesale_price}/kg
                  </span>
                </div>
              </div>
              {/* Other mandis */}
              <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 'var(--s-2)' }}>
                {(comparisonData.comparison || []).map(m => (
                  <div key={m.region_id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 'var(--s-3)', borderRadius: 'var(--r-md)', background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)' }}>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 'var(--text-sm)' }}>{m.mandi_name}</div>
                      <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>{m.state}</div>
                    </div>
                    <span style={{ fontWeight: 700, fontSize: 'var(--text-sm)' }}>₹{m.wholesale_price}/kg</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: 'var(--s-10)', fontSize: 'var(--text-sm)' }}>
              No comparison data available.
            </div>
          )}
        </div>
      </div>

      {/* ── Item Detail Modal ── */}
      <Modal
        show={!!selectedRecDetails}
        onClose={() => setSelectedRecDetails(null)}
        title={selectedRecDetails ? `${selectedRecDetails.item_name} Analysis` : ''}
      >
        {selectedRecDetails && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--s-4)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
                {t.currentStock}: {selectedRecDetails.stock_kg || 45} kg
              </span>
              <Badge variant={selectedRecDetails.risk_score > 66 ? 'danger' : selectedRecDetails.risk_score > 33 ? 'warning' : 'success'}>
                Risk: {selectedRecDetails.risk_score?.toFixed(0)}%
              </Badge>
            </div>

            {selectedRecDetails.gemini_active && selectedRecDetails.gemini_details ? (
              <>
                <div style={{ borderLeft: '3px solid var(--accent-solid)', paddingLeft: 'var(--s-4)' }}>
                  <div style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: 'var(--accent-solid)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 'var(--s-1)' }}>AI Pricing</div>
                  <p style={{ fontWeight: 700, fontSize: 'var(--text-sm)' }}>{selectedRecDetails.gemini_details.recommendation}</p>
                </div>
                {[
                  { label: 'Business Rationale', color: 'var(--text-secondary)', val: selectedRecDetails.gemini_details.business_explanation },
                  { label: 'Risks', color: 'var(--danger)', val: selectedRecDetails.gemini_details.risks },
                  { label: 'Suggestions', color: 'var(--success)', val: selectedRecDetails.gemini_details.suggestions },
                ].map(item => (
                  <div key={item.label}>
                    <div style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: item.color, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 'var(--s-1)' }}>{item.label}</div>
                    <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{item.val}</p>
                  </div>
                ))}
              </>
            ) : (
              <>
                <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)', lineHeight: 1.7 }}>{selectedRecDetails.explanation}</p>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--s-3)' }}>
                  {[
                    { label: 'Max Temperature', val: `${selectedRecDetails.temperature || 31}°C` },
                    { label: 'Humidity', val: `${selectedRecDetails.humidity || 65}%` },
                  ].map(item => (
                    <div key={item.label} style={{ background: 'var(--bg-elevated)', padding: 'var(--s-3)', borderRadius: 'var(--r-md)' }}>
                      <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginBottom: 2 }}>{item.label}</div>
                      <div style={{ fontWeight: 700, fontSize: 'var(--text-sm)' }}>{item.val}</div>
                    </div>
                  ))}
                </div>
                <div style={{ background: 'var(--bg-elevated)', padding: 'var(--s-3)', borderRadius: 'var(--r-md)' }}>
                  <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginBottom: 2 }}>Forecast</div>
                  <div style={{ fontSize: 'var(--text-sm)' }}>
                    Expected demand: <strong>{selectedRecDetails.forecast_demand_today?.toFixed(1) || 20} kg</strong>
                  </div>
                </div>
              </>
            )}

            <Button variant="primary" style={{ width: '100%', marginTop: 'var(--s-2)' }} onClick={() => setSelectedRecDetails(null)}>
              {t.close}
            </Button>
          </div>
        )}
      </Modal>

      {/* ── AI Report Modal ── */}
      <AIReport
        show={showReport}
        onClose={() => setShowReport(false)}
        regionName={summaryData?.raw_data?.market || 'Local APMC'}
        recommendations={recs}
        weather={summaryData?.raw_data?.weather}
        summary={summaryData?.summary}
        language={language}
      />
    </div>
  )
}
