import React, { useState, useEffect } from 'react'
import Badge from '../components/ui/Badge.jsx'
import Button from '../components/ui/Button.jsx'

const TRANSLATIONS = {
  en: {
    title: 'Inventory Analytics', subtitle: 'Real-time stock tracking with AI-powered purchase optimization',
    search: 'Search inventory, forecasts, recommendations…', product: 'Product', stock: 'Stock',
    spoilage: 'Spoilage Risk', demand: 'Daily Demand', daysRemaining: 'Days Left',
    recPrice: 'Rec. Price', procurement: 'Procurement', aiSuggestion: 'AI Suggestion',
    lowStock: 'Low Stock', adequate: 'Healthy', critical: 'Critical', moderate: 'Moderate', days: 'd',
    noResults: 'No items match your search.',
  },
  hi: {
    title: 'स्टॉक विश्लेषण', subtitle: 'वास्तविक समय स्टॉक ट्रैकिंग और AI खरीद अनुकूलन',
    search: 'स्टॉक खोजें…', product: 'उत्पाद', stock: 'स्टॉक',
    spoilage: 'खराबी जोखिम', demand: 'दैनिक मांग', daysRemaining: 'शेष दिन',
    recPrice: 'सिफारिशित मूल्य', procurement: 'खरीद', aiSuggestion: 'AI सुझाव',
    lowStock: 'कम स्टॉक', adequate: 'पर्याप्त', critical: 'गंभीर', moderate: 'मध्यम', days: 'दिन',
    noResults: 'कोई आइटम नहीं मिला।',
  },
  ta: {
    title: 'சரக்கு பகுப்பாய்வு', subtitle: 'நிகழ்நேர சரக்கு கண்காணிப்பு மற்றும் AI கொள்முதல் மேம்படுத்தல்',
    search: 'சரக்கு தேடு…', product: 'தயாரிப்பு', stock: 'இருப்பு',
    spoilage: 'கெட்டுப்போகும் ஆபத்து', demand: 'தினசரி தேவை', daysRemaining: 'மீதமுள்ள நாட்கள்',
    recPrice: 'பரிந்துரைக்கப்பட்ட விலை', procurement: 'கொள்முதல்', aiSuggestion: 'AI பரிந்துரை',
    lowStock: 'குறைந்த இருப்பு', adequate: 'போதுமானது', critical: 'அவசரம்', moderate: 'மிதமான', days: 'நாட்கள்',
    noResults: 'தேடலுடன் பொருந்தும் பொருட்கள் இல்லை.',
  },
}

const CATEGORY_ICONS = { vegetable: '🥬', fruit: '🍎', grain: '🌾', spice: '🌶️', flower: '🌸', other: '📦' }

export default function InventoryPage({ regionId, language }) {
  const [inventory, setInventory] = useState(null)
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  const t = TRANSLATIONS[language] || TRANSLATIONS.en

  useEffect(() => {
    setLoading(true)
    fetch(`/api/inventory/${regionId}?lang=${language}`)
      .then(r => { if (!r.ok) throw new Error('Failed'); return r.json() })
      .then(d => { setInventory(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [regionId, language])

  const getRiskBadge = (score) => {
    if (score > 66) return <Badge variant="danger">Critical</Badge>
    if (score > 33) return <Badge variant="warning">Moderate</Badge>
    return <Badge variant="success">Healthy</Badge>
  }

  const getStockBadge = (item) =>
    item.low_stock_warning
      ? <Badge variant="danger">{t.lowStock}</Badge>
      : <Badge variant="success">{t.adequate}</Badge>

  const filteredInventory = (inventory || []).filter(item => {
    const q = searchQuery.toLowerCase()
    return (
      item.item_name.toLowerCase().includes(q) ||
      item.category.toLowerCase().includes(q) ||
      item.ai_purchase_suggestion.toLowerCase().includes(q)
    )
  })

  if (loading) {
    return (
      <div className="page-content">
        <div className="pg-header">
          <div>
            <div className="skeleton-line" style={{ width: 200, height: 26, marginBottom: 8 }} />
            <div className="skeleton-line" style={{ width: 280, height: 14 }} />
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--s-3)', marginTop: 'var(--s-6)' }}>
          {[1, 2, 3, 4, 5].map(i => <div key={i} className="skeleton-card" style={{ height: 64 }} />)}
        </div>
      </div>
    )
  }

  return (
    <div className="page-content">
      {/* Header */}
      <div className="pg-header">
        <div className="pg-header-left">
          <h2 className="pg-title">{t.title}</h2>
          <p className="pg-subtitle">{t.subtitle}</p>
        </div>
      </div>

      {/* Search */}
      <div className="search-container">
        <span className="material-symbols-rounded">search</span>
        <input
          type="text"
          className="search-field"
          placeholder={t.search}
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

      {/* Stats bar */}
      {inventory && (
        <div style={{ display: 'flex', gap: 'var(--s-3)', marginBottom: 'var(--s-4)', flexWrap: 'wrap' }}>
          <Badge variant="muted">{inventory.length} products</Badge>
          <Badge variant="danger">{inventory.filter(i => i.spoilage_risk > 66).length} critical</Badge>
          <Badge variant="warning">{inventory.filter(i => i.low_stock_warning).length} low stock</Badge>
          <Badge variant="success">{inventory.filter(i => !i.low_stock_warning && i.spoilage_risk <= 33).length} healthy</Badge>
        </div>
      )}

      {/* Table */}
      {filteredInventory.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: 'var(--s-10)' }}>
          <span className="material-symbols-rounded" style={{ fontSize: 40, color: 'var(--text-muted)' }}>inventory_2</span>
          <p style={{ marginTop: 'var(--s-3)', color: 'var(--text-secondary)', fontSize: 'var(--text-sm)' }}>{t.noResults}</p>
        </div>
      ) : (
        <div className="table-container">
          <table className="modern-table">
            <thead>
              <tr>
                <th>{t.product}</th>
                <th>{t.stock}</th>
                <th>{t.spoilage}</th>
                <th>{t.demand}</th>
                <th>{t.daysRemaining}</th>
                <th>{t.recPrice}</th>
                <th>{t.procurement}</th>
                <th>{t.aiSuggestion}</th>
              </tr>
            </thead>
            <tbody>
              {filteredInventory.map(item => {
                const emoji = CATEGORY_ICONS[item.category?.toLowerCase()] || '📦'
                const daysColor = item.days_remaining < 1.5 ? 'var(--danger)' : item.days_remaining < 3 ? 'var(--warning)' : 'var(--text-primary)'
                return (
                  <tr key={item.item_id}>
                    {/* Product */}
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--s-3)' }}>
                        <span style={{ fontSize: 20 }}>{emoji}</span>
                        <div>
                          <div style={{ fontWeight: 700, fontSize: 'var(--text-sm)' }}>{item.item_name}</div>
                          <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', textTransform: 'capitalize' }}>{item.category}</div>
                        </div>
                      </div>
                    </td>
                    {/* Stock */}
                    <td>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                        <span style={{ fontWeight: 700, fontSize: 'var(--text-sm)' }}>{item.stock} {item.unit || 'kg'}</span>
                        {getStockBadge(item)}
                      </div>
                    </td>
                    {/* Spoilage */}
                    <td>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                        <span style={{ fontWeight: 700, fontSize: 'var(--text-sm)', color: item.spoilage_risk > 66 ? 'var(--danger)' : item.spoilage_risk > 33 ? 'var(--warning)' : 'var(--text-primary)' }}>
                          {item.spoilage_risk.toFixed(0)}%
                        </span>
                        {getRiskBadge(item.spoilage_risk)}
                      </div>
                    </td>
                    {/* Demand */}
                    <td>
                      <span style={{ fontWeight: 600, fontSize: 'var(--text-sm)' }}>{item.expected_demand.toFixed(1)} {item.unit || 'kg'}/d</span>
                    </td>
                    {/* Days left */}
                    <td>
                      <span style={{ fontWeight: 700, color: daysColor, fontSize: 'var(--text-sm)' }}>
                        {item.days_remaining}{t.days}
                      </span>
                    </td>
                    {/* Rec price */}
                    <td>
                      <div>
                        <div style={{ fontWeight: 800, color: 'var(--accent-solid)', fontSize: '0.95rem' }}>₹{item.recommended_selling_price}</div>
                        <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>Wholesale: ₹{item.mandi_price}</div>
                      </div>
                    </td>
                    {/* Procurement */}
                    <td>
                      <div style={{ fontSize: 'var(--text-sm)' }}>
                        <div>Planned: <strong>{item.planned_purchase || 0} {item.unit || 'kg'}</strong></div>
                        <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>AI: <strong>{item.recommended_purchase || 0} {item.unit || 'kg'}</strong></div>
                      </div>
                    </td>
                    {/* AI suggestion */}
                    <td style={{ maxWidth: 160 }}>
                      <span style={{
                        fontSize: 'var(--text-xs)', fontWeight: 600, lineHeight: 1.5,
                        color: item.low_stock_warning ? 'var(--warning)' : item.spoilage_risk > 66 ? 'var(--danger)' : 'var(--text-secondary)',
                      }}>
                        {item.ai_purchase_suggestion}
                      </span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
