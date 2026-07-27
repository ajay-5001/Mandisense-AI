import React, { useState, useRef, useEffect } from 'react'
import { getApiUrl } from '../utils/api'

const TRANSLATIONS = {
  en: {
    assistantName: "MandiSense AI",
    statusOnline: "Online Assistant",
    placeholder: "Ask anything about pricing...",
    suggestedTitle: "Ask MandiSense:",
    voiceListening: "Listening...",
    close: "Close",
    chatGreeting: "Hello! I am your AI Business Assistant. How can I help you today?",
    q1: "Should I reduce tomato price?",
    q2: "What should I buy tomorrow?",
    q3: "Which product is most profitable?",
    q4: "Why are sales decreasing?",
    q5: "Which product has highest spoilage risk?",
    q6: "How can I increase today's profit?",
  },
  hi: {
    assistantName: "मंडीसेंस AI",
    statusOnline: "ऑनलाइन सहायक",
    placeholder: "कीमतों के बारे में कुछ भी पूछें...",
    suggestedTitle: "मंडीसेंस से पूछें:",
    voiceListening: "सुन रहा हूँ...",
    close: "बंद करें",
    chatGreeting: "नमस्ते! मैं आपका AI व्यापार सहायक हूँ। आज मैं आपकी क्या मदद कर सकता हूँ?",
    q1: "क्या मुझे टमाटर के दाम कम करने चाहिए?",
    q2: "मुझे कल क्या खरीदना चाहिए?",
    q3: "कौन सा उत्पाद सबसे अधिक लाभदायक है?",
    q4: "बिक्री क्यों कम हो रही है?",
    q5: "किस उत्पाद में खराब होने का सबसे अधिक खतरा है?",
    q6: "मैं आज का लाभ कैसे बढ़ा सकता हूँ?",
  },
  ta: {
    assistantName: "மண்டிசென்ஸ் AI",
    statusOnline: "ஆன்லைன் உதவியாளர்",
    placeholder: "விலை பற்றி ஏதாவது கேளுங்கள்...",
    suggestedTitle: "மண்டிசென்ஸிடம் கேளுங்கள்:",
    voiceListening: "கேட்கிறேன்...",
    close: "மூடு",
    chatGreeting: "வணக்கம்! நான் உங்கள் AI வணிக உதவியாளர். இன்று நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?",
    q1: "தக்காளி விலையை குறைக்க வேண்டுமா?",
    q2: "நாளை நான் என்ன வாங்க வேண்டும்?",
    q3: "எந்த தயாரிப்பு மிகவும் லாபகரமானது?",
    q4: "விற்பனை ஏன் குறைகிறது?",
    q5: "எந்த பொருளுக்கு கெட்டுப்போகும் ஆபத்து அதிகம்?",
    q6: "இன்றைய லாபத்தை எவ்வாறு அதிகரிப்பது?",
  }
}

export default function ChatAssistant({ regionId, language }) {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [loading, setLoading] = useState(false)
  const chatBodyRef = useRef(null)
  const recognitionRef = useRef(null)

  const t = TRANSLATIONS[language] || TRANSLATIONS.en

  // Load API Key from LocalStorage
  const getApiKey = () => localStorage.getItem('gemini_api_key') || ''

  useEffect(() => {
    // Initial message
    setMessages([
      { id: 'greet', sender: 'assistant', text: t.chatGreeting }
    ])
  }, [language])

  useEffect(() => {
    if (chatBodyRef.current) {
      chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight
    }
  }, [messages])

  const handleSend = async (textToSend) => {
    if (!textToSend.trim()) return

    const userMessage = { id: Date.now().toString(), sender: 'user', text: textToSend }
    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setLoading(true)

    // Format chat history
    const history = messages
      .filter(m => m.id !== 'greet')
      .map(m => ({ sender: m.sender, text: m.text }))

    try {
      const apiKey = getApiKey()
      const res = await fetch(getApiUrl('/api/chat'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(apiKey && { 'X-Gemini-Key': apiKey })
        },
        body: JSON.stringify({
          query: textToSend,
          region_id: regionId,
          language: language,
          history: history
        })
      })

      if (!res.ok) throw new Error('API request failed')
      const data = await res.json()
      
      const assistantMessage = { id: (Date.now() + 1).toString(), sender: 'assistant', text: data.response }
      setMessages(prev => [...prev, assistantMessage])
      
      // Auto speak out response
      speakText(data.response)
    } catch (err) {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: language === 'hi' ? 'उत्तर प्राप्त करने में असमर्थ। कृपया बाद में प्रयास करें।' : language === 'ta' ? 'பதில் பெற முடியவில்லை. பின்னர் முயற்சிக்கவும்.' : 'Unable to get response. Please check your setup.'
      }])
    } finally {
      setLoading(false)
    }
  }

  const speakText = (text) => {
    if (!('speechSynthesis' in window)) return
    window.speechSynthesis.cancel()

    const utterance = new SpeechSynthesisUtterance(text)
    const langCodes = { en: 'en-IN', hi: 'hi-IN', ta: 'ta-IN' }
    utterance.lang = langCodes[language] || 'en-IN'
    utterance.rate = 0.95
    utterance.pitch = 1.0
    window.speechSynthesis.speak(utterance)
  }

  const toggleVoice = () => {
    if (isListening) {
      if (recognitionRef.current) recognitionRef.current.stop()
      setIsListening(false)
      return
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      alert('Speech recognition is not supported in this browser. Please try Chrome.')
      return
    }

    const recognition = new SpeechRecognition()
    const langCodes = { en: 'en-IN', hi: 'hi-IN', ta: 'ta-IN' }
    recognition.lang = langCodes[language] || 'en-IN'
    recognition.interimResults = false
    recognition.maxAlternatives = 1

    recognition.onstart = () => {
      setIsListening(true)
    }

    recognition.onresult = (event) => {
      const speechToText = event.results[0][0].transcript
      setInputValue(speechToText)
      handleSend(speechToText)
    }

    recognition.onerror = (event) => {
      console.error('Speech error:', event.error)
      setIsListening(false)
    }

    recognition.onend = () => {
      setIsListening(false)
    }

    recognitionRef.current = recognition
    recognition.start()
  }

  return (
    <>
      {/* Floating Action Button */}
      <button 
        className="chat-assistant-toggle"
        onClick={() => {
          setIsOpen(!isOpen)
          window.speechSynthesis?.cancel()
        }}
        title="AI Assistant"
      >
        <span className="material-symbols-rounded" style={{ fontSize: '28px' }}>
          {isOpen ? 'close' : 'forum'}
        </span>
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="chat-window">
          {/* Header */}
          <div className="chat-header">
            <div className="chat-header-info">
              <div className="logo-pulse" style={{ width: '30px', height: '30px' }}>
                <span className="material-symbols-rounded" style={{ fontSize: '18px' }}>eco</span>
              </div>
              <div>
                <h4 style={{ fontSize: '0.9rem', fontWeight: '800' }}>{t.assistantName}</h4>
                <span style={{ fontSize: '0.7rem', opacity: 0.8 }}>{t.statusOnline}</span>
              </div>
            </div>
            <button 
              style={{ background: 'transparent', border: 'none', color: 'white', cursor: 'pointer' }}
              onClick={() => setIsOpen(false)}
            >
              <span className="material-symbols-rounded">keyboard_arrow_down</span>
            </button>
          </div>

          {/* Chat Messages Body */}
          <div className="chat-body" ref={chatBodyRef}>
            {messages.map((m) => (
              <div key={m.id} className={`chat-message ${m.sender}`}>
                {m.text}
              </div>
            ))}
            {loading && (
              <div className="chat-message assistant" style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                <span className="loading-spinner" style={{ width: '14px', height: '14px', borderWidth: '2px' }} />
                <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  {language === 'hi' ? 'सोच रहा हूँ...' : language === 'ta' ? 'யோசிக்கிறேன்...' : 'Thinking...'}
                </span>
              </div>
            )}
          </div>

          {/* Suggested Quick Questions */}
          <div className="chat-suggested-questions">
            <button className="chat-suggested-btn" onClick={() => handleSend(t.q1)}>{t.q1}</button>
            <button className="chat-suggested-btn" onClick={() => handleSend(t.q2)}>{t.q2}</button>
            <button className="chat-suggested-btn" onClick={() => handleSend(t.q3)}>{t.q3}</button>
            <button className="chat-suggested-btn" onClick={() => handleSend(t.q5)}>{t.q5}</button>
          </div>

          {/* Input Area */}
          <div className="chat-input-area">
            <button 
              className={`chat-btn voice-rec ${isListening ? 'listening' : ''}`}
              onClick={toggleVoice}
              title="Voice input"
            >
              <span className="material-symbols-rounded">
                {isListening ? 'graphic_eq' : 'mic'}
              </span>
            </button>
            
            <input 
              type="text" 
              className="chat-input"
              placeholder={isListening ? t.voiceListening : t.placeholder}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleSend(inputValue)
              }}
              disabled={isListening}
            />

            <button 
              className="chat-btn"
              onClick={() => handleSend(inputValue)}
              title="Send Message"
            >
              <span className="material-symbols-rounded">send</span>
            </button>
          </div>
        </div>
      )}
    </>
  )
}
