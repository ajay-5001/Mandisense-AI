import React, { useState, useEffect } from 'react'
import Modal from '../components/ui/Modal.jsx'
import Button from '../components/ui/Button.jsx'
import Badge from '../components/ui/Badge.jsx'
import Dropdown from '../components/ui/Dropdown.jsx'
import { getApiUrl } from '../utils/api'

const CATEGORIES = ['vegetable', 'fruit', 'grain', 'spice', 'flower', 'other']
const CATEGORY_ICONS = { vegetable: '🥬', fruit: '🍎', grain: '🌾', spice: '🌶️', flower: '🌸', other: '📦' }

const FormField = ({ label, children }) => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--s-2)' }}>
    <label className="form-label">{label}</label>
    {children}
  </div>
)

export default function ProductsPage({ language }) {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingProduct, setEditingProduct] = useState(null)
  const [name, setName] = useState('')
  const [category, setCategory] = useState('vegetable')
  const [unit, setUnit] = useState('kg')
  const [purchasePrice, setPurchasePrice] = useState(0)
  const [sellingPrice, setSellingPrice] = useState(0)
  const [currentStock, setCurrentStock] = useState(0)
  const [supplierName, setSupplierName] = useState('')

  const loadProducts = () => {
    setLoading(true)
    fetch(getApiUrl('/api/products'))
      .then(r => r.json())
      .then(d => { setProducts(d); setLoading(false) })
      .catch(() => setLoading(false))
  }

  useEffect(() => { loadProducts() }, [])

  const handleOpenAdd = () => {
    setEditingProduct(null); setName(''); setCategory('vegetable'); setUnit('kg')
    setPurchasePrice(0); setSellingPrice(0); setCurrentStock(0); setSupplierName('')
    setShowModal(true)
  }

  const handleOpenEdit = (p) => {
    setEditingProduct(p); setName(p.name); setCategory(p.category); setUnit(p.unit)
    setPurchasePrice(p.purchase_price); setSellingPrice(p.selling_price)
    setCurrentStock(p.current_stock); setSupplierName(p.supplier_name || '')
    setShowModal(true)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    const payload = { name, category, unit, purchase_price: parseFloat(purchasePrice), selling_price: parseFloat(sellingPrice), current_stock: parseFloat(currentStock), supplier_name: supplierName || null }
    const url = editingProduct ? `/api/products/${editingProduct.id}` : '/api/products'
    const method = editingProduct ? 'PUT' : 'POST'
    fetch(getApiUrl(url), { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      .then(r => { if (!r.ok) throw new Error('Failed'); return r.json() })
      .then(() => { setShowModal(false); loadProducts() })
      .catch(err => alert(err.message))
  }

  const handleDelete = (id) => {
    if (!window.confirm('Delete this product? All related data will be removed.')) return
    fetch(getApiUrl(`/api/products/${id}`), { method: 'DELETE' }).then(() => loadProducts()).catch(err => alert(err.message))
  }

  const filtered = products.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.category.toLowerCase().includes(search.toLowerCase())
  )



  return (
    <div className="page-content">
      {/* Header */}
      <div className="pg-header">
        <div className="pg-header-left">
          <h2 className="pg-title">Catalog Manager</h2>
          <p className="pg-subtitle">Configure your product stock, pricing, and categories. Mandi forecasts adapt to this catalog.</p>
        </div>
        <Button variant="primary" icon="add" onClick={handleOpenAdd}>Add Product</Button>
      </div>

      {/* Search */}
      <div className="search-container">
        <span className="material-symbols-rounded">search</span>
        <input
          type="text"
          className="search-field"
          placeholder="Search products by name or category…"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        {search && (
          <button onClick={() => setSearch('')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', display: 'flex' }}>
            <span className="material-symbols-rounded" style={{ fontSize: 18 }}>close</span>
          </button>
        )}
      </div>

      {/* Stats */}
      {!loading && (
        <div style={{ display: 'flex', gap: 'var(--s-2)', marginBottom: 'var(--s-4)', flexWrap: 'wrap' }}>
          <Badge variant="muted">{filtered.length} products</Badge>
          {CATEGORIES.map(cat => {
            const cnt = filtered.filter(p => p.category === cat).length
            return cnt > 0 ? <Badge key={cat} variant="accent">{CATEGORY_ICONS[cat]} {cat} ({cnt})</Badge> : null
          })}
        </div>
      )}

      {/* Product Grid */}
      {loading ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 'var(--s-4)' }}>
          {[1, 2, 3].map(i => <div key={i} className="skeleton-card" style={{ height: 160 }} />)}
        </div>
      ) : filtered.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: 'var(--s-10)' }}>
          <span className="material-symbols-rounded" style={{ fontSize: 48, color: 'var(--text-muted)' }}>storefront</span>
          <p style={{ color: 'var(--text-secondary)', marginTop: 'var(--s-3)', fontSize: 'var(--text-sm)' }}>No products found. Click "Add Product" to start.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 'var(--s-4)' }}>
          {filtered.map(p => {
            const emoji = CATEGORY_ICONS[p.category?.toLowerCase()] || '📦'
            const margin = p.selling_price > p.purchase_price
              ? (((p.selling_price - p.purchase_price) / p.purchase_price) * 100).toFixed(0)
              : 0
            return (
              <div key={p.id} className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--s-3)' }}>
                {/* Top */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--s-3)' }}>
                    <span style={{ fontSize: 28 }}>{emoji}</span>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: 'var(--text-h3)' }}>{p.name}</div>
                      <Badge variant="info" style={{ marginTop: 3 }}>{p.category}</Badge>
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: 'var(--s-1)' }}>
                    <Button variant="ghost" size="sm" icon="edit" onClick={() => handleOpenEdit(p)} style={{ padding: 'var(--s-1)', minWidth: 32 }} />
                    <Button variant="danger" size="sm" icon="delete" onClick={() => handleDelete(p.id)} style={{ padding: 'var(--s-1)', minWidth: 32 }} />
                  </div>
                </div>
                {/* Price grid */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--s-2)' }}>
                  {[
                    { label: 'Wholesale', val: `₹${p.purchase_price}/${p.unit}`, color: 'var(--text-primary)' },
                    { label: 'Selling', val: `₹${p.selling_price}/${p.unit}`, color: 'var(--accent-solid)' },
                    { label: 'Stock', val: `${p.current_stock} ${p.unit}`, color: 'var(--text-primary)' },
                    { label: 'Supplier', val: p.supplier_name || 'N/A', color: 'var(--text-primary)' },
                  ].map(item => (
                    <div key={item.label} style={{ background: 'var(--bg-elevated)', padding: 'var(--s-2) var(--s-3)', borderRadius: 'var(--r-sm)' }}>
                      <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginBottom: 2, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>{item.label}</div>
                      <div style={{ fontWeight: 700, fontSize: 'var(--text-sm)', color: item.color, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{item.val}</div>
                    </div>
                  ))}
                </div>
                {/* Margin badge */}
                <Badge variant={parseInt(margin) > 20 ? 'success' : parseInt(margin) > 0 ? 'warning' : 'danger'} style={{ alignSelf: 'flex-start' }}>
                  {margin > 0 ? `+${margin}% margin` : 'No margin'}
                </Badge>
              </div>
            )
          })}
        </div>
      )}

      {/* Add / Edit Modal */}
      <Modal
        show={showModal}
        onClose={() => setShowModal(false)}
        title={editingProduct ? 'Edit Product' : 'Add New Product'}
        maxWidth="480px"
      >
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--s-4)' }}>
          <FormField label="Product Name">
            <input type="text" required className="modern-input" placeholder="e.g. Tomato, Rice, Rose" value={name} onChange={e => setName(e.target.value)} />
          </FormField>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--s-3)' }}>
            <FormField label="Category">
              <Dropdown
                value={category}
                onChange={setCategory}
                options={CATEGORIES.map(cat => ({ value: cat, label: `${CATEGORY_ICONS[cat]} ${cat.charAt(0).toUpperCase() + cat.slice(1)}` }))}
              />
            </FormField>
            <FormField label="Unit">
              <input type="text" required className="modern-input" placeholder="e.g. kg, box" value={unit} onChange={e => setUnit(e.target.value)} />
            </FormField>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--s-3)' }}>
            <FormField label="Wholesale Price (₹)">
              <input type="number" step="0.01" required className="modern-input" value={purchasePrice} onChange={e => setPurchasePrice(e.target.value)} />
            </FormField>
            <FormField label="Selling Price (₹)">
              <input type="number" step="0.01" required className="modern-input" value={sellingPrice} onChange={e => setSellingPrice(e.target.value)} />
            </FormField>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--s-3)' }}>
            <FormField label="Current Stock">
              <input type="number" step="0.1" required className="modern-input" value={currentStock} onChange={e => setCurrentStock(e.target.value)} />
            </FormField>
            <FormField label="Supplier Name">
              <input type="text" className="modern-input" placeholder="Optional" value={supplierName} onChange={e => setSupplierName(e.target.value)} />
            </FormField>
          </div>

          <div style={{ display: 'flex', gap: 'var(--s-3)', marginTop: 'var(--s-2)' }}>
            <Button type="button" variant="ghost" style={{ flex: 1 }} onClick={() => setShowModal(false)}>Cancel</Button>
            <Button type="submit" variant="primary" style={{ flex: 1 }} icon="save">Save Product</Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
