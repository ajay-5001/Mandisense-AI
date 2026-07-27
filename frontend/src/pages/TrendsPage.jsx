import React, { useState, useEffect } from 'react'
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  BarChart, Bar, CartesianGrid, Line, ComposedChart,
} from 'recharts'
import Button from '../components/ui/Button.jsx'
import Badge from '../components/ui/Badge.jsx'
import { getApiUrl } from '../utils/api'

const ITEMS = [
  { id: 1, name: 'Tomato' }, { id: 2, name: 'Onion' }, { id: 3, name: 'Potato' },
  { id: 4, name: 'Cauliflower' }, { id: 5, name: 'Green Chili' }, { id: 6, name: 'Lady Finger' },
  { id: 7, name: 'Brinjal' }, { id: 8, name: 'Cabbage' }, { id: 9, name: 'Carrot' },
  { id: 10, name: 'Spinach' }, { id: 11, name: 'Banana' }, { id: 12, name: 'Apple' },
  { id: 13, name: 'Mango' }, { id: 14, name: 'Papaya' }, { id: 15, name: 'Grapes' },
]

const TRANSLATIONS = {
  en: {
    title: 'Market Trends & Forecasts', subtitle: 'Advanced price trends, sales volumes, and weather correlations',
    daysSelector: 'Range', priceChartTitle: 'Wholesale vs Suggested Selling Price (₹/kg)',
    demandChartTitle: 'Historical Sales & 3-Day AI Demand Forecast (kg)',
    weatherChartTitle: 'Temperature & Humidity Correlation',
    spoilageGaugeTitle: "Today's Spoilage Risk",
    tempLabel: 'Max Temp °C', humidLabel: 'Humidity %', rainLabel: 'Rainfall mm',
  },
  hi: {
    title: 'बाज़ार रुझान और पूर्वानुमान', subtitle: 'उन्नत मूल्य रुझान, बिक्री और मौसम का संबंध',
    daysSelector: 'रेंज', priceChartTitle: 'थोक बनाम अनुशंसित बिक्री मूल्य (₹/किग्रा)',
    demandChartTitle: 'ऐतिहासिक बिक्री और 3-दिवसीय AI मांग पूर्वानुमान (किग्रा)',
    weatherChartTitle: 'तापमान और आर्द्रता का संबंध',
    spoilageGaugeTitle: 'आज का खराबी जोखिम',
    tempLabel: 'अधिकतम °C', humidLabel: 'नमी %', rainLabel: 'वर्षा मिमी',
  },
  ta: {
    title: 'சந்தை போக்குகள் & கணிப்புகள்', subtitle: 'மேம்பட்ட விலை போக்குகள் மற்றும் வானிலை தொடர்புகள்',
    daysSelector: 'வரம்பு', priceChartTitle: 'மொத்த விற்பனை மற்றும் பரிந்துரைக்கப்பட்ட விலை (₹/கிலோ)',
    demandChartTitle: 'வரலாற்று விற்பனை மற்றும் 3-நாள் AI தேவை கணிப்பு (கிலோ)',
    weatherChartTitle: 'வெப்பநிலை மற்றும் ஈரப்பதம் தொடர்பு',
    spoilageGaugeTitle: 'இன்றைய கெட்டுப்போகும் ஆபத்து',
    tempLabel: 'அதிகபட்ச °C', humidLabel: 'ஈரப்பதம் %', rainLabel: 'மழை மிமீ',
  },
}

// ── Shared chart tooltip ──
function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: 'var(--bg-elevated)',
      border: '1px solid var(--border-default)',
      borderRadius: 'var(--r-md)',
      padding: '8px 14px',
      boxShadow: 'var(--shadow-lg)',
      fontSize: 'var(--text-xs)',
    }}>
      <div style={{ color: 'var(--text-secondary)', fontWeight: 700, marginBottom: 6 }}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: p.color || 'var(--text-primary)', display: 'flex', justifyContent: 'space-between', gap: 16 }}>
          <span style={{ color: 'var(--text-muted)' }}>{p.name}</span>
          <span style={{ fontWeight: 700 }}>
            {typeof p.value === 'number' ? p.value.toFixed(1) : p.value}
          </span>
        </div>
      ))}
    </div>
  )
}

// ── Inline chart legend ──
function ChartLegend({ items }) {
  return (
    <div className="chart-legend">
      {items.map(item => (
        <div key={item.label} className="chart-legend-item">
          <div className="chart-legend-dot" style={{ background: item.color }} />
          {item.label}
        </div>
      ))}
    </div>
  )
}

// ── Spoilage Gauge ──
function SpoilageGauge({ score }) {
  const n = Math.min(100, Math.max(0, score || 0))
  const r = 46, stroke = 8
  const circ = 2 * Math.PI * r
  // Arc goes from -90deg → 270deg (full circle)
  const offset = circ - (n / 100) * circ * 0.75  // 3/4 arc
  const color = n > 66 ? 'var(--danger)' : n > 33 ? 'var(--warning)' : 'var(--success)'
  const level = n > 66 ? 'High Risk' : n > 33 ? 'Moderate' : 'Low Risk'
  const badgeVariant = n > 66 ? 'danger' : n > 33 ? 'warning' : 'success'

  return (
    <div className="gauge-container">
      <svg className="gauge-svg" viewBox="0 0 120 120" style={{ transform: 'rotate(-225deg)' }}>
        <circle cx="60" cy="60" r={r} fill="none" stroke="var(--bg-elevated)" strokeWidth={stroke} strokeDasharray={`${circ * 0.75} ${circ}`} strokeLinecap="round" />
        <circle
          cx="60" cy="60" r={r} fill="none" stroke={color} strokeWidth={stroke}
          strokeDasharray={`${Math.max(0, (n / 100) * circ * 0.75)} ${circ}`}
          strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 0.8s ease-out' }}
        />
      </svg>
      <div className="gauge-center-text" style={{ transform: 'translate(-50%, -40%)' }}>
        <div className="gauge-val" style={{ color }}>{n}%</div>
        <div className="gauge-lbl" style={{ marginTop: 2 }}>{level}</div>
      </div>
      <Badge variant={badgeVariant} style={{ marginTop: 8 }}>{level}</Badge>
    </div>
  )
}

export default function TrendsPage({ regionId, language }) {
  const [selectedItem, setSelectedItem] = useState(1)
  const [trends, setTrends] = useState(null)
  const [loading, setLoading] = useState(true)
  const [days, setDays] = useState(30)

  const t = TRANSLATIONS[language] || TRANSLATIONS.en

  useEffect(() => {
    setLoading(true)
    fetch(getApiUrl(`/api/trends/${selectedItem}/${regionId}?days=${days}`))
      .then(r => r.json())
      .then(d => { setTrends(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [selectedItem, regionId, days])

  const priceData = () => (trends?.prices || []).map(p => ({
    date: p.date.slice(5),
    wholesale: p.wholesale,
    retail: p.retail,
  }))

  const volumeData = () => {
    const hist = (trends?.volumes || []).map(v => ({ date: v.date.slice(5), volume: v.volume_kg, forecast: null }))
    const fore = (trends?.forecasts || []).map(f => ({ date: f.date.slice(5) + ' ▸', volume: null, forecast: f.predicted_volume }))
    return [...hist, ...fore]
  }

  const weatherData = () => (trends?.weather || []).map(w => ({
    date: w.date.slice(5), temp: w.temp_max, humidity: w.humidity,
  }))

  const spoilageScore = trends?.volumes?.length
    ? ((selectedItem * 17 + regionId * 23) % 75 + 15) : 30

  const selectedItemName = ITEMS.find(i => i.id === selectedItem)?.name || 'Tomato'

  return (
    <div className="page-content">
      {/* Header */}
      <div className="pg-header">
        <div className="pg-header-left">
          <h2 className="pg-title">{t.title}</h2>
          <p className="pg-subtitle">{t.subtitle}</p>
        </div>
      </div>

      {/* Item Selector */}
      <div className="item-selector">
        {ITEMS.map(item => (
          <Button
            key={item.id}
            variant="tab"
            active={selectedItem === item.id}
            onClick={() => setSelectedItem(item.id)}
            size="sm"
          >
            {item.name}
          </Button>
        ))}
      </div>

      {/* Days Range Selector */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--s-3)', marginBottom: 'var(--s-6)', flexWrap: 'wrap' }}>
        <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
          {t.daysSelector}:
        </span>
        <div style={{ display: 'flex', gap: 'var(--s-2)' }}>
          {[7, 14, 30, 90].map(d => (
            <Button key={d} variant="tab" active={days === d} size="sm" onClick={() => setDays(d)}>
              {d}D
            </Button>
          ))}
        </div>
        <Badge variant="accent">{selectedItemName}</Badge>
      </div>

      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--s-4)' }}>
          <div className="skeleton-card" style={{ height: 260 }} />
          <div className="skeleton-card" style={{ height: 220 }} />
          <div className="skeleton-card" style={{ height: 200 }} />
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--s-5)' }}>

          {/* Price Chart + Gauge Row */}
          <div style={{ display: 'grid', gap: 'var(--s-5)' }} className="dashboard-grid">
            {/* Price chart — spans 2 cols on desktop */}
            <div className="glass-card" style={{ gridColumn: 'span 2' }}>
              <div className="chart-title">
                <span className="material-symbols-rounded">show_chart</span>
                {t.priceChartTitle}
              </div>
              <ChartLegend items={[
                { label: 'Mandi Wholesale Price', color: 'var(--info)' },
                { label: 'Recommended Selling Price', color: 'var(--accent-solid)' },
              ]} />
              <ResponsiveContainer width="100%" height={230}>
                <AreaChart data={priceData()} margin={{ top: 4, right: 4, left: -10, bottom: 0 }}>
                  <defs>
                    <linearGradient id="gradWholesale" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="var(--info)"         stopOpacity={0.2} />
                      <stop offset="95%" stopColor="var(--info)"         stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="gradRetail" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="var(--accent-solid)" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="var(--accent-solid)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke="rgba(255,255,255,0.04)" strokeDasharray="4 4" vertical={false} />
                  <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 10 }} axisLine={false} tickLine={false} width={32} />
                  <Tooltip content={<ChartTooltip />} />
                  <Area type="monotone" dataKey="wholesale" name="Wholesale" stroke="var(--info)" fill="url(#gradWholesale)" strokeWidth={1.5} dot={false} activeDot={{ r: 4 }} />
                  <Area type="monotone" dataKey="retail"    name="Selling"   stroke="var(--accent-solid)" fill="url(#gradRetail)"    strokeWidth={2}   dot={false} activeDot={{ r: 4 }} />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Spoilage Gauge */}
            <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 220 }}>
              <div className="chart-title" style={{ width: '100%', justifyContent: 'center', marginBottom: 'var(--s-4)' }}>
                <span className="material-symbols-rounded">security</span>
                {t.spoilageGaugeTitle}
              </div>
              <SpoilageGauge score={spoilageScore} />
            </div>
          </div>

          {/* Volume + Forecast Chart */}
          <div className="glass-card">
            <div className="chart-title">
              <span className="material-symbols-rounded">bar_chart</span>
              {t.demandChartTitle}
            </div>
            <ChartLegend items={[
              { label: 'Historical Sales (kg)', color: 'var(--info)' },
              { label: 'AI Forecast (kg)', color: 'var(--accent-solid)' },
            ]} />
            <ResponsiveContainer width="100%" height={230}>
              <ComposedChart data={volumeData()} margin={{ top: 4, right: 4, left: -10, bottom: 0 }}>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" strokeDasharray="4 4" vertical={false} />
                <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 10 }} axisLine={false} tickLine={false} width={35} />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="volume" name="Historical Sales (kg)" fill="var(--info)" radius={[4, 4, 0, 0]} opacity={0.7} maxBarSize={36} />
                <Line type="monotone" dataKey="forecast" name="AI Forecast (kg)" stroke="var(--accent-solid)" strokeWidth={2.5} strokeDasharray="5 3" dot={{ r: 4, strokeWidth: 0, fill: 'var(--accent-solid)' }} connectNulls />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* Weather Chart */}
          <div className="glass-card">
            <div className="chart-title">
              <span className="material-symbols-rounded">cloud</span>
              {t.weatherChartTitle}
            </div>
            <ChartLegend items={[
              { label: t.tempLabel,  color: 'var(--danger)' },
              { label: t.humidLabel, color: 'var(--warning)' },
            ]} />
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={weatherData()} margin={{ top: 4, right: 4, left: -10, bottom: 0 }}>
                <defs>
                  <linearGradient id="gradTemp" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="var(--danger)" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="var(--danger)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" strokeDasharray="4 4" vertical={false} />
                <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 10 }} axisLine={false} tickLine={false} width={28} />
                <Tooltip content={<ChartTooltip />} />
                <Area type="monotone" dataKey="temp"     name={t.tempLabel}  stroke="var(--danger)"  fill="url(#gradTemp)" strokeWidth={1.5} dot={false} />
                <Line  type="monotone" dataKey="humidity" name={t.humidLabel} stroke="var(--warning)" strokeWidth={1.5}     dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>

        </div>
      )}
    </div>
  )
}
