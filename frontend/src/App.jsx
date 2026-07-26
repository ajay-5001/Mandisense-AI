import React, { useState, useEffect } from 'react'
import TodayPage from './pages/TodayPage.jsx'
import InventoryPage from './pages/InventoryPage.jsx'
import TrendsPage from './pages/TrendsPage.jsx'
import SettingsPage from './pages/SettingsPage.jsx'
import ProductsPage from './pages/ProductsPage.jsx'
import ChatAssistant from './components/ChatAssistant.jsx'
import MandiPricesPage from './pages/MandiPricesPage.jsx'

const REGIONS = [
  { id: 1,  name: 'Azadpur Mandi',              state: 'Delhi',                district: 'Central Delhi' },
  { id: 2,  name: 'Koyambedu Market',            state: 'Tamil Nadu',           district: 'Chennai' },
  { id: 3,  name: 'Vashi APMC',                  state: 'Maharashtra',          district: 'Mumbai' },
  { id: 4,  name: 'Yeshwanthpur APMC',            state: 'Karnataka',            district: 'Bengaluru' },
  { id: 5,  name: 'Jamalpur Market',              state: 'Gujarat',              district: 'Ahmedabad' },
  { id: 6,  name: 'Bowenpally APMC',              state: 'Telangana',            district: 'Hyderabad' },
  { id: 7,  name: 'Madanapalle Tomato Market',    state: 'Andhra Pradesh',       district: 'Chittoor' },
  { id: 8,  name: 'Kala Dera Mandi',              state: 'Rajasthan',            district: 'Jaipur' },
  { id: 9,  name: 'Kolkata APMC',                 state: 'West Bengal',          district: 'Kolkata' },
  { id: 10, name: 'Naveen Galla Mandi',           state: 'Uttar Pradesh',        district: 'Lucknow' },
  { id: 11, name: 'Ludhiana APMC',                state: 'Punjab',               district: 'Ludhiana' },
  { id: 12, name: 'Karnal Grain Market',           state: 'Haryana',              district: 'Karnal' },
  { id: 13, name: 'Karond Mandi',                  state: 'Madhya Pradesh',       district: 'Bhopal' },
  { id: 14, name: 'Chalai Market',                 state: 'Kerala',               district: 'Thiruvananthapuram' },
  { id: 15, name: 'Bazar Samiti Mandi',            state: 'Bihar',                district: 'Patna' },
  { id: 16, name: 'Chhatra Bazar',                 state: 'Odisha',               district: 'Cuttack' },
  { id: 17, name: 'Pamohi APMC',                   state: 'Assam',                district: 'Kamrup' },
  { id: 18, name: 'Krishi Upaj Mandi',             state: 'Jharkhand',            district: 'Ranchi' },
  { id: 19, name: 'Pandri Mandi',                  state: 'Chhattisgarh',         district: 'Raipur' },
  { id: 20, name: 'Niranjanpur Mandi',             state: 'Uttarakhand',          district: 'Dehradun' },
  { id: 21, name: 'Dhalli Mandi',                  state: 'Himachal Pradesh',     district: 'Shimla' },
  { id: 22, name: 'Narwal Fruit Market',           state: 'Jammu & Kashmir',      district: 'Jammu' },
  { id: 23, name: 'Panaji APMC',                   state: 'Goa',                  district: 'North Goa' },
  { id: 24, name: 'Khwairamband Bazar',            state: 'Manipur',              district: 'Imphal West' },
  { id: 25, name: 'Maharajganj Bazar',             state: 'Tripura',              district: 'West Tripura' },
  { id: 26, name: 'Iewduh Market',                 state: 'Meghalaya',            district: 'East Khasi Hills' },
  { id: 27, name: 'Dimapur APMC',                  state: 'Nagaland',             district: 'Dimapur' },
  { id: 28, name: 'Bara Bazar',                    state: 'Mizoram',              district: 'Aizawl' },
  { id: 29, name: 'Lal Market',                    state: 'Sikkim',               district: 'East Sikkim' },
  { id: 30, name: 'Puducherry Grand Market',       state: 'Puducherry',           district: 'Puducherry' },
  { id: 31, name: 'Sector 26 APMC',               state: 'Chandigarh',           district: 'Chandigarh' },
  { id: 32, name: 'Leh Vegetable Market',          state: 'Ladakh',               district: 'Leh' },
  { id: 33, name: 'Port Blair APMC',              state: 'Andaman & Nicobar',    district: 'South Andaman' },
  { id: 34, name: 'Daman APMC',                   state: 'Dadra & Nagar Haveli', district: 'Daman' },
  { id: 35, name: 'Kavaratti Market',             state: 'Lakshadweep',          district: 'Lakshadweep' },
]

const NAV_ITEMS_ANALYTICS = [
  { id: 'today',       icon: 'dashboard',     labelKey: 'today' },
  { id: 'inventory',  icon: 'inventory_2',   labelKey: 'inventory' },
  { id: 'products',   icon: 'storefront',    labelKey: 'products' },
  { id: 'trends',     icon: 'trending_up',   labelKey: 'trends' },
]

const NAV_ITEMS_MARKET = [
  { id: 'mandiprice', icon: 'price_change',  labelKey: 'mandiprice' },
]

const NAV_ITEMS_SYSTEM = [
  { id: 'settings',   icon: 'settings',      labelKey: 'settings' },
]

// All nav items flattened (for mobile bottom nav)
const NAV_ITEMS_MOBILE = [
  { id: 'today',      icon: 'dashboard',    labelKey: 'today' },
  { id: 'inventory', icon: 'inventory_2',  labelKey: 'inventory' },
  { id: 'trends',    icon: 'trending_up',  labelKey: 'trends' },
  { id: 'mandiprice', icon: 'price_change', labelKey: 'mandiprice' },
  { id: 'settings',  icon: 'settings',     labelKey: 'settings' },
]

const NAV_LABELS = {
  en: { today: 'Dashboard', inventory: 'Inventory', products: 'Catalog',     trends: 'Trends',     mandiprice: 'Mandi Prices', settings: 'Settings' },
  hi: { today: 'डैशबोर्ड',    inventory: 'स्टॉक',     products: 'उत्पाद सूची', trends: 'रुझान',       mandiprice: 'मंडी मूल्य',    settings: 'सेटिंग्स' },
  ta: { today: 'டாஷ்போர்டு',  inventory: 'இருப்பு',   products: 'பட்டியல்',    trends: 'போக்குகள்', mandiprice: 'மண்டி விலை',  settings: 'அமைப்புகள்' },
}

export default function App() {
  const [activePage, setActivePage] = useState('today')
  const [language, setLanguage] = useState('en')
  const [regionId, setRegionId] = useState(1)
  const [theme, setTheme] = useState('dark')

  const currentRegion = REGIONS.find(r => r.id === regionId) || REGIONS[0]
  const labels = NAV_LABELS[language] || NAV_LABELS.en

  // Load persisted preferences
  useEffect(() => {
    const cachedLang = localStorage.getItem('language')
    if (cachedLang) setLanguage(cachedLang)

    const cachedRegion = localStorage.getItem('region_id')
    if (cachedRegion) setRegionId(parseInt(cachedRegion))

    const cachedTheme = localStorage.getItem('theme') || 'dark'
    setTheme(cachedTheme)
    document.body.classList.toggle('light-theme', cachedTheme === 'light')
  }, [])

  useEffect(() => {
    localStorage.setItem('region_id', regionId.toString())
  }, [regionId])

  const toggleLanguage = () => {
    const next = language === 'en' ? 'hi' : language === 'hi' ? 'ta' : 'en'
    setLanguage(next)
    localStorage.setItem('language', next)
  }

  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark'
    setTheme(next)
    localStorage.setItem('theme', next)
    document.body.classList.toggle('light-theme', next === 'light')
  }

  const renderPage = () => {
    switch (activePage) {
      case 'today':      return <TodayPage regionId={regionId} language={language} />
      case 'inventory':  return <InventoryPage regionId={regionId} language={language} />
      case 'products':   return <ProductsPage language={language} />
      case 'trends':     return <TrendsPage regionId={regionId} language={language} />
      case 'mandiprice': return <MandiPricesPage />
      case 'settings':
        return (
          <SettingsPage
            regionId={regionId}
            setRegionId={setRegionId}
            language={language}
            setLanguage={setLanguage}
            regions={REGIONS}
          />
        )
      default: return <TodayPage regionId={regionId} language={language} />
    }
  }

  return (
    <div className="app-container">

      {/* ── Desktop Sidebar ── */}
      <aside className="desktop-sidebar">
        {/* Logo */}
        <div className="sidebar-logo">
          <div className="logo-pulse">
            <span className="material-symbols-rounded">eco</span>
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '1rem', letterSpacing: '-0.02em' }}>MandiSense</div>
            <div style={{ fontSize: '0.625rem', color: 'var(--text-muted)', fontWeight: 500, marginTop: 1 }}>AI Price Intelligence</div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="sidebar-nav">
          <div className="sidebar-section-label">Analytics</div>
          {NAV_ITEMS_ANALYTICS.map(item => (
            <button
              key={item.id}
              className={`sidebar-item ${activePage === item.id ? 'active' : ''}`}
              onClick={() => setActivePage(item.id)}
            >
              <span className="material-symbols-rounded">{item.icon}</span>
              {labels[item.labelKey]}
            </button>
          ))}

          <div className="sidebar-section-label">Market Intelligence</div>
          {NAV_ITEMS_MARKET.map(item => (
            <button
              key={item.id}
              className={`sidebar-item ${activePage === item.id ? 'active' : ''}`}
              onClick={() => setActivePage(item.id)}
            >
              <span className="material-symbols-rounded">{item.icon}</span>
              {labels[item.labelKey]}
            </button>
          ))}

          <div className="sidebar-section-label">System</div>
          {NAV_ITEMS_SYSTEM.map(item => (
            <button
              key={item.id}
              className={`sidebar-item ${activePage === item.id ? 'active' : ''}`}
              onClick={() => setActivePage(item.id)}
            >
              <span className="material-symbols-rounded">{item.icon}</span>
              {labels[item.labelKey]}
            </button>
          ))}
        </nav>

        {/* Footer — region + controls */}
        <div className="sidebar-footer">
          <button
            className="sidebar-region-chip"
            onClick={() => setActivePage('settings')}
            style={{ background: 'none', border: '1px solid var(--border-subtle)', cursor: 'pointer', width: '100%', textAlign: 'left' }}
          >
            <span className="material-symbols-rounded" style={{ fontSize: 14, color: 'var(--accent-solid)', flexShrink: 0 }}>location_on</span>
            <span className="region-name" style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', fontWeight: 500 }}>
              {currentRegion.name}
            </span>
          </button>

          <div className="sidebar-controls">
            <button className="sidebar-ctrl-btn" onClick={toggleLanguage} title="Switch language">
              <span className="material-symbols-rounded" style={{ fontSize: 14 }}>language</span>
              {language.toUpperCase()}
            </button>
            <button className="sidebar-ctrl-btn" onClick={toggleTheme} title="Toggle theme">
              <span className="material-symbols-rounded" style={{ fontSize: 14 }}>
                {theme === 'dark' ? 'light_mode' : 'dark_mode'}
              </span>
              {theme === 'dark' ? 'Light' : 'Dark'}
            </button>
          </div>
        </div>
      </aside>

      {/* ── Main Area ── */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>

        {/* Mobile Header */}
        <header className="app-header">
          <div className="header-brand">
            <div className="logo-pulse" style={{ width: 30, height: 30 }}>
              <span className="material-symbols-rounded" style={{ fontSize: 17 }}>eco</span>
            </div>
            <div>
              <h1>MandiSense</h1>
              <span className="header-tagline">AI Price Intel</span>
            </div>
          </div>
          <button className="header-region" onClick={() => setActivePage('settings')}>
            <span className="material-symbols-rounded" style={{ fontSize: 14 }}>location_on</span>
            <span style={{ fontWeight: 600 }}>{currentRegion.name.split(' ')[0]}</span>
          </button>
        </header>

        {/* Page Content */}
        <main className="main-content">
          {renderPage()}
        </main>
      </div>

      {/* ── Mobile Bottom Nav ── */}
      <nav className="bottom-nav">
        {NAV_ITEMS_MOBILE.map(item => (
          <button
            key={item.id}
            className={`nav-item ${activePage === item.id ? 'active' : ''}`}
            onClick={() => setActivePage(item.id)}
          >
            <span className="material-symbols-rounded">{item.icon}</span>
            <span>{labels[item.labelKey]}</span>
          </button>
        ))}
      </nav>

      {/* ── Floating AI Chat ── */}
      <ChatAssistant regionId={regionId} language={language} />
    </div>
  )
}
