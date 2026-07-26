import React, { useState, useRef, useEffect } from 'react'

/**
 * VoiceButton — Voice input/output component
 * 
 * Uses the Web Speech API (browser-native, no paid API):
 * - SpeechRecognition for STT (speech-to-text)
 * - SpeechSynthesis for TTS (text-to-speech)
 * 
 * Vendor can speak queries like "how should I price onions today?"
 * and get a spoken response.
 */

export default function VoiceButton({ recommendations, language }) {
  const [listening, setListening] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [response, setResponse] = useState('')
  const recognitionRef = useRef(null)

  // Language mapping for speech APIs
  const langCodes = { en: 'en-IN', hi: 'hi-IN', ta: 'ta-IN' }

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      setResponse('Voice input is not supported in this browser. Try Chrome.')
      setShowModal(true)
      return
    }

    const recognition = new SpeechRecognition()
    recognition.lang = langCodes[language] || 'en-IN'
    recognition.interimResults = false
    recognition.maxAlternatives = 1

    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript.toLowerCase()
      setTranscript(text)
      handleVoiceQuery(text)
    }

    recognition.onerror = (event) => {
      setListening(false)
      setResponse(`Could not hear you. Please try again. (${event.error})`)
    }

    recognition.onend = () => {
      setListening(false)
    }

    recognitionRef.current = recognition
    recognition.start()
    setListening(true)
    setShowModal(true)
    setTranscript('')
    setResponse('')
  }

  const handleVoiceQuery = (query) => {
    if (!recommendations?.length) {
      setResponse('No data available. Please wait for recommendations to load.')
      return
    }

    // Simple keyword matching to find the right item
    const matchedRec = recommendations.find(rec =>
      query.includes(rec.item_name.toLowerCase())
    )

    if (matchedRec) {
      const answer = matchedRec.explanation || matchedRec.summary
      setResponse(answer)
      speak(answer)
    } else {
      // Default: give top recommendation
      const topRec = recommendations[0]
      const answer = topRec.explanation || topRec.summary
      const prefix = language === 'hi'
        ? 'सबसे ज़रूरी सिफारिश: '
        : language === 'ta'
        ? 'மிக முக்கியமான பரிந்துரை: '
        : 'Top recommendation: '
      setResponse(prefix + answer)
      speak(prefix + answer)
    }
  }

  const speak = (text) => {
    if (!('speechSynthesis' in window)) return
    
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = langCodes[language] || 'en-IN'
    utterance.rate = 0.9
    utterance.pitch = 1.0
    window.speechSynthesis.speak(utterance)
  }

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
    }
    window.speechSynthesis?.cancel()
    setListening(false)
    setShowModal(false)
  }

  return (
    <>
      {/* Floating Action Button */}
      <button
        className={`voice-fab ${listening ? 'listening' : ''}`}
        onClick={listening ? stopListening : startListening}
        title="Voice input"
      >
        🎙️
      </button>

      {/* Voice Modal */}
      {showModal && (
        <div className="voice-overlay" onClick={(e) => {
          if (e.target === e.currentTarget) stopListening()
        }}>
          <div className="voice-modal">
            <div className="voice-icon-large">
              {listening ? '🔴' : '🎙️'}
            </div>
            <div className="voice-status">
              {listening
                ? (language === 'hi' ? 'सुन रहा हूँ...' : language === 'ta' ? 'கேட்கிறேன்...' : 'Listening...')
                : (language === 'hi' ? 'जवाब' : language === 'ta' ? 'பதில்' : 'Response')
              }
            </div>
            <div className="voice-transcript">
              {transcript && (
                <div style={{ marginBottom: '8px', color: 'var(--text-primary)', fontStyle: 'italic' }}>
                  "{transcript}"
                </div>
              )}
              {response && (
                <div style={{ color: 'var(--accent-green)' }}>
                  {response}
                </div>
              )}
              {!transcript && !response && listening && (
                <div style={{ color: 'var(--text-muted)' }}>
                  {language === 'hi'
                    ? '"प्याज़ का दाम क्या रखूं?" बोलें'
                    : language === 'ta'
                    ? '"தக்காளி விலை என்ன?" என்று சொல்லுங்கள்'
                    : 'Try saying "how should I price onions today?"'
                  }
                </div>
              )}
            </div>
            <button className="voice-close-btn" onClick={stopListening}>
              {language === 'hi' ? 'बंद करें' : language === 'ta' ? 'மூடு' : 'Close'}
            </button>
          </div>
        </div>
      )}
    </>
  )
}
