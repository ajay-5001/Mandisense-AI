import React, { useState, useEffect } from 'react'
import Badge from '../components/ui/Badge.jsx'
import Button from '../components/ui/Button.jsx'
import Dropdown from '../components/ui/Dropdown.jsx'

const TRANSLATIONS = {
  en: {
    title: 'System Settings', subtitle: 'Configure your AI assistant, region, and notification preferences',
    apiSection: 'Gemini AI Configuration', apiLabel: 'API Key',
    apiPlaceholder: 'Enter your Gemini API key (AI-xxxxxxx)',
    apiHelp: 'Stored locally in browser. Never transmitted outside direct Gemini API calls.',
    themeSection: 'Visual Theme', langSection: 'Display Language',
    regionSection: 'Market Region', regionSub: 'Select your state/UT and district to choose from available agricultural wholesale mandis.',
    stateLabel: 'State / Union Territory', districtLabel: 'District', mandiLabel: 'Available Mandis',
    notifySection: 'Notification Preferences',
    notifLowStock: 'Low Stock Inventory Alerts', notifSpoilage: 'High Spoilage Risk Warnings', notifRain: 'Weather Disruption Signals',
    voiceSection: 'Voice Assistant', voiceFeedback: 'Text-to-Speech Responses', voiceSpeed: 'Voice Speed Rate',
    modelSection: 'Forecast Engine', modelLabel: 'Active Core Model',
    light: 'Light Mode', dark: 'Dark Mode', saved: 'Settings saved',
  },
  hi: {
    title: 'सिस्टम सेटिंग्स', subtitle: 'AI सहायक, क्षेत्र और अधिसूचना प्राथमिकताएं कॉन्फ़िगर करें',
    apiSection: 'Gemini AI कॉन्फ़िगरेशन', apiLabel: 'API कुंजी',
    apiPlaceholder: 'जेमिनी API कुंजी दर्ज करें',
    apiHelp: 'ब्राउज़र में स्थानीय रूप से संग्रहीत। जेमिनी API कॉल के बाहर कभी नहीं भेजा जाता।',
    themeSection: 'दृश्य थीम', langSection: 'प्रदर्शन भाषा',
    regionSection: 'बाज़ार क्षेत्र', regionSub: 'अपने राज्य/केंद्रशासित प्रदेश और जिले का चयन करें।',
    stateLabel: 'राज्य / केंद्रशासित प्रदेश', districtLabel: 'जिला', mandiLabel: 'उपलब्ध मंडियां',
    notifySection: 'अधिसूचना प्राथमिकताएं',
    notifLowStock: 'कम स्टॉक अलर्ट', notifSpoilage: 'खराबी जोखिम चेतावनी', notifRain: 'मौसम व्यवधान सिग्नल',
    voiceSection: 'वॉयस असिस्टेंट', voiceFeedback: 'TTS आवाज प्रतिक्रियाएं', voiceSpeed: 'आवाज गति',
    modelSection: 'पूर्वानुमान इंजन', modelLabel: 'सक्रिय मॉडल',
    light: 'लाइट मोड', dark: 'डार्क मोड', saved: 'सेटिंग्स सहेजी गईं',
  },
  ta: {
    title: 'கணினி அமைப்புகள்', subtitle: 'AI உதவியாளர், பகுதி மற்றும் அறிவிப்பு விருப்பங்களை உள்ளமைக்கவும்',
    apiSection: 'Gemini AI உள்ளமைவு', apiLabel: 'API விசை',
    apiPlaceholder: 'ஜெமினி API விசையை உள்ளிடவும்',
    apiHelp: 'உலாவியில் உள்ளூரில் சேமிக்கப்படும். ஜெமினி API அழைப்புகளுக்கு வெளியே அனுப்பப்படாது.',
    themeSection: 'காட்சி தீம்', langSection: 'காட்சி மொழி',
    regionSection: 'சந்தை பகுதி', regionSub: 'உங்கள் மாநிலம் மற்றும் மாவட்டத்தை தேர்ந்தெடுக்கவும்.',
    stateLabel: 'மாநிலம் / யூனியன் பிரதேசம்', districtLabel: 'மாவட்டம்', mandiLabel: 'கிடைக்கும் மண்டிகள்',
    notifySection: 'அறிவிப்பு விருப்பங்கள்',
    notifLowStock: 'குறைந்த இருப்பு அறிவிப்புகள்', notifSpoilage: 'கெட்டுப்போகும் ஆபத்து எச்சரிக்கைகள்', notifRain: 'வானிலை இடையூறு சமிக்ஞைகள்',
    voiceSection: 'குரல் உதவியாளர்', voiceFeedback: 'TTS குரல் பதில்கள்', voiceSpeed: 'குரல் வேகம்',
    modelSection: 'கணிப்பு இயந்திரம்', modelLabel: 'செயலில் உள்ள மாதிரி',
    light: 'ஒளி பயன்முறை', dark: 'இருண்ட பயன்முறை', saved: 'அமைப்புகள் சேமிக்கப்பட்டன',
  },
}

function SettingsSection({ icon, title, children }) {
  return (
    <div className="settings-section">
      <div className="settings-section-header">
        <div className="settings-section-icon">
          <span className="material-symbols-rounded">{icon}</span>
        </div>
        <span className="settings-section-title">{title}</span>
      </div>
      <div className="settings-section-body">
        {children}
      </div>
    </div>
  )
}

function Toggle({ checked, onChange }) {
  return (
    <label className="toggle-switch">
      <input type="checkbox" checked={checked} onChange={e => onChange(e.target.checked)} />
      <div className="toggle-track">
        <div className="toggle-thumb" />
      </div>
    </label>
  )
}

export default function SettingsPage({ regionId, setRegionId, language, setLanguage, regions }) {
  const [apiKey, setApiKey] = useState('')
  const [showKey, setShowKey] = useState(false)
  const [theme, setTheme] = useState('dark')
  const [notifStock, setNotifStock] = useState(true)
  const [notifSpoil, setNotifSpoil] = useState(true)
  const [notifWeather, setNotifWeather] = useState(true)
  const [voiceTTS, setVoiceTTS] = useState(true)
  const [voiceSpeedVal, setVoiceSpeedVal] = useState(0.95)
  const [forecastModel, setForecastModel] = useState('holt_winters')
  const [saveMsg, setSaveMsg] = useState(false)
  const currentRegion = regions.find(r => r.id === regionId) || regions[0]
  const [selectedState, setSelectedState] = useState(currentRegion?.state || '')
  const [selectedDistrict, setSelectedDistrict] = useState(currentRegion?.district || '')
  const t = TRANSLATIONS[language] || TRANSLATIONS.en

  useEffect(() => {
    if (currentRegion) { setSelectedState(currentRegion.state); setSelectedDistrict(currentRegion.district || '') }
  }, [regionId, regions])

  useEffect(() => {
    setApiKey(localStorage.getItem('gemini_api_key') || '')
    const th = localStorage.getItem('theme') || 'dark'; setTheme(th)
    setNotifStock(localStorage.getItem('notif_stock') !== 'false')
    setNotifSpoil(localStorage.getItem('notif_spoil') !== 'false')
    setNotifWeather(localStorage.getItem('notif_weather') !== 'false')
    setVoiceTTS(localStorage.getItem('voice_tts') !== 'false')
    setVoiceSpeedVal(parseFloat(localStorage.getItem('voice_speed') || '0.95'))
    setForecastModel(localStorage.getItem('forecast_model') || 'holt_winters')
  }, [])

  const toast = () => { setSaveMsg(true); setTimeout(() => setSaveMsg(false), 2000) }
  const persist = (key, val) => { localStorage.setItem(key, val); toast() }

  const handleTheme = (th) => {
    setTheme(th); localStorage.setItem('theme', th)
    document.body.classList.toggle('light-theme', th === 'light'); toast()
  }

  const handleLang = (code) => { setLanguage(code); persist('language', code) }

  const states = [...new Set(regions.map(r => r.state))].sort()
  const districts = [...new Set(regions.filter(r => r.state === selectedState).map(r => r.district))].filter(Boolean).sort()
  const mandis = regions.filter(r => r.state === selectedState && (!selectedDistrict || selectedDistrict === 'All Districts' || r.district === selectedDistrict))

  return (
    <div className="page-content">
      {/* Header */}
      <div className="pg-header">
        <div className="pg-header-left">
          <h2 className="pg-title">{t.title}</h2>
          <p className="pg-subtitle">{t.subtitle}</p>
        </div>
      </div>

      {/* Toast */}
      {saveMsg && (
        <div style={{
          position: 'fixed', top: 20, right: 20, zIndex: 1000,
          background: 'var(--accent-gradient)', color: 'white',
          padding: 'var(--s-3) var(--s-5)', borderRadius: 'var(--r-md)',
          boxShadow: 'var(--shadow-accent)', fontWeight: 700, fontSize: 'var(--text-sm)',
          animation: 'slideUpIn 0.3s ease',
        }}>
          <span className="material-symbols-rounded" style={{ fontSize: 16, marginRight: 6, verticalAlign: 'middle' }}>check_circle</span>
          {t.saved}
        </div>
      )}

      {/* Gemini API Key */}
      <SettingsSection icon="key" title={t.apiSection}>
        <label className="form-label">{t.apiLabel}</label>
        <div style={{ position: 'relative' }}>
          <input
            type={showKey ? 'text' : 'password'}
            className="modern-input"
            placeholder={t.apiPlaceholder}
            value={apiKey}
            onChange={e => { setApiKey(e.target.value); persist('gemini_api_key', e.target.value) }}
            style={{ paddingRight: 40 }}
          />
          <button
            onClick={() => setShowKey(v => !v)}
            style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', display: 'flex' }}
          >
            <span className="material-symbols-rounded" style={{ fontSize: 18 }}>{showKey ? 'visibility_off' : 'visibility'}</span>
          </button>
        </div>
        <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', lineHeight: 1.5 }}>{t.apiHelp}</p>
      </SettingsSection>

      {/* Theme */}
      <SettingsSection icon="palette" title={t.themeSection}>
        <div style={{ display: 'flex', gap: 'var(--s-3)' }}>
          <Button variant={theme === 'light' ? 'primary' : 'ghost'} style={{ flex: 1 }} icon="light_mode" onClick={() => handleTheme('light')}>{t.light}</Button>
          <Button variant={theme === 'dark' ? 'primary' : 'ghost'} style={{ flex: 1 }} icon="dark_mode" onClick={() => handleTheme('dark')}>{t.dark}</Button>
        </div>
      </SettingsSection>

      {/* Language */}
      <SettingsSection icon="language" title={t.langSection}>
        <div style={{ display: 'flex', gap: 'var(--s-3)' }}>
          {[{ code: 'en', label: 'English' }, { code: 'hi', label: 'हिन्दी' }, { code: 'ta', label: 'தமிழ்' }].map(lang => (
            <Button key={lang.code} variant={language === lang.code ? 'primary' : 'ghost'} style={{ flex: 1 }} onClick={() => handleLang(lang.code)}>
              {lang.label}
            </Button>
          ))}
        </div>
      </SettingsSection>

      {/* Region Selector */}
      <SettingsSection icon="location_on" title={t.regionSection}>
        <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', lineHeight: 1.5, marginBottom: 'var(--s-2)' }}>{t.regionSub}</p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--s-3)' }}>
          <div>
            <label className="form-label">{t.stateLabel}</label>
            <Dropdown
              value={selectedState}
              onChange={(val) => {
                setSelectedState(val)
                const first = regions.find(r => r.state === val)
                if (first) { setSelectedDistrict(first.district || ''); setRegionId(first.id); toast() }
              }}
              options={states.map(s => ({ value: s, label: s }))}
            />
          </div>
          <div>
            <label className="form-label">{t.districtLabel}</label>
            <Dropdown
              value={selectedDistrict}
              onChange={(val) => {
                setSelectedDistrict(val)
                const first = regions.find(r => r.state === selectedState && r.district === val)
                if (first) { setRegionId(first.id); toast() }
              }}
              options={[{ value: 'All Districts', label: 'All Districts' }, ...districts.map(d => ({ value: d, label: d }))]}
            />
          </div>
          <div>
            <label className="form-label">{t.mandiLabel}</label>
            <Dropdown
              value={regionId}
              onChange={(val) => { setRegionId(parseInt(val)); toast() }}
              options={mandis.map(m => ({ value: m.id, label: m.name }))}
            />
          </div>
          <Badge variant="accent" icon="check">{currentRegion?.name}</Badge>
        </div>
      </SettingsSection>

      {/* Notifications */}
      <SettingsSection icon="notifications" title={t.notifySection}>
        {[
          { label: t.notifLowStock, key: 'notif_stock', val: notifStock, set: setNotifStock },
          { label: t.notifSpoilage, key: 'notif_spoil', val: notifSpoil, set: setNotifSpoil },
          { label: t.notifRain, key: 'notif_weather', val: notifWeather, set: setNotifWeather },
        ].map(item => (
          <div key={item.key} className="settings-row">
            <span className="settings-row-label">{item.label}</span>
            <Toggle checked={item.val} onChange={(v) => { item.set(v); persist(item.key, v.toString()) }} />
          </div>
        ))}
      </SettingsSection>

      {/* Voice */}
      <SettingsSection icon="record_voice_over" title={t.voiceSection}>
        <div className="settings-row">
          <span className="settings-row-label">{t.voiceFeedback}</span>
          <Toggle checked={voiceTTS} onChange={(v) => { setVoiceTTS(v); persist('voice_tts', v.toString()) }} />
        </div>
        <div className="settings-row">
          <span className="settings-row-label">{t.voiceSpeed}</span>
          <Dropdown
            value={voiceSpeedVal}
            onChange={(v) => { setVoiceSpeedVal(parseFloat(v)); persist('voice_speed', v.toString()) }}
            options={[{ value: 0.8, label: '0.8× Slow' }, { value: 0.95, label: '1.0× Normal' }, { value: 1.15, label: '1.25× Fast' }]}
            width="140px"
          />
        </div>
      </SettingsSection>

      {/* Forecast Model */}
      <SettingsSection icon="model_training" title={t.modelSection}>
        <div className="settings-row">
          <span className="settings-row-label">{t.modelLabel}</span>
          <Dropdown
            value={forecastModel}
            onChange={(v) => { setForecastModel(v); persist('forecast_model', v) }}
            options={[
              { value: 'holt_winters', label: 'Holt-Winters' },
              { value: 'arima', label: 'ARIMA (Exogenous)' },
              { value: 'prophet', label: 'Prophet Model' },
            ]}
            width="180px"
          />
        </div>
      </SettingsSection>
    </div>
  )
}
