import { useState, useEffect } from 'react'
import { startGame, sendAction, shutdownGame } from './api'
import Layout from './components/Layout'
import Terminal from './components/Terminal'
import InputConsole from './components/InputConsole'
import StatusHUD from './components/StatusHUD'
import ChoiceGrid from './components/ChoiceGrid'
import GlitchText from './components/GlitchText'
import BootSequence from './components/BootSequence'
import MindMap from './components/MindMap'
import TitleScreen from './components/TitleScreen'
import AudioManager from './components/AudioManager'
import VHSEffect from './components/VHSEffect'
import './App.css'

function App() {
  const [showTitle, setShowTitle] = useState(true)
  const [booting, setBooting] = useState(false)
  const [history, setHistory] = useState([])
  const [uiState, setUiState] = useState(null)
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [showBoard, setShowBoard] = useState(false)

  const handleStartGame = () => {
    setShowTitle(false)
    setBooting(true)
  }

  const handleTitleExit = async () => {
    await shutdownGame()
    setTimeout(() => {
      window.close()
      document.body.innerHTML = "<div style='background:black;color:red;height:100vh;display:flex;align-items:center;justify-content:center;font-family:monospace'>NO_SIGNAL</div>"
    }, 500)
  }

  useEffect(() => {
    if (!showTitle && !booting) {
      initGame()
    }
  }, [showTitle, booting])

  const initGame = async () => {
    setLoading(true)
    try {
      const data = await startGame()
      if (data) {
        setHistory([{ type: 'output', text: data.output }])
        setUiState(data.state)
      }
    } catch (e) {
      setHistory([{ type: 'output', text: "ERROR: CONNECTION_LOST_TO_MAINFRAME" }])
    }
    setLoading(false)
  }

  const handleSend = async (txt) => {
    if (!txt) return

    setHistory(prev => [...prev, { type: 'input', text: `> ${txt}` }])

    setLoading(true)
    try {
      const data = await sendAction(txt)
      if (data) {
        setHistory(prev => [...prev, { type: 'output', text: data.output }])
        setUiState(data.state)
      }
    } catch (e) {
      setHistory(prev => [...prev, { type: 'output', text: "ERROR: SIGNAL_INTERRUPTED" }])
    }
    setLoading(false)
    setInput("")
  }

  const handleShutdown = async () => {
    setHistory(prev => [...prev, { type: 'output', text: "INITIATING_SHUTDOWN_SEQUENCE..." }])
    await shutdownGame()
    setTimeout(() => {
      window.close() // Try to close tab
      // If script can't close, show offline state
      document.body.innerHTML = "<div style='background:black;color:red;height:100vh;display:flex;align-items:center;justify-content:center;font-family:monospace'>NO_SIGNAL</div>"
    }, 1000)
  }

  const getCurrentMusic = () => {
    if (showTitle) return "main_theme.mp3"
    return uiState?.music
  }

  return (
    <>
      <AudioManager
        music={getCurrentMusic()}
        sfxQueue={uiState?.sfx_queue}
        fearLevel={uiState?.fear_level}
        mentalLoad={uiState?.mental_load}
      />

      <VHSEffect
        active={!showTitle}
        mentalLoad={uiState?.mental_load}
        attention={uiState?.attention_level}
        disorientation={uiState?.psych_flags?.disorientation}
        instability={uiState?.psych_flags?.instability}
      />

      {showTitle && (
        <TitleScreen onStart={handleStartGame} onExit={handleTitleExit} />
      )}

      {!showTitle && booting && (
        <BootSequence onComplete={() => setBooting(false)} />
      )}

      {!showTitle && !booting && (
        <div className={`app-theme-wrapper theme-${uiState?.archetype || 'neutral'}`}>
          <Layout
            uiState={uiState}
            sidebar={<StatusHUD uiState={uiState} />}
          >
            <div className="main-feed">
              <div className="header-deco">
                <GlitchText text="TYGER_TYGER_LIAR_LIAR" className="title-glitch" />
                <div className="system-status">
                  SYS.ONLINE
                  <span className="ctrl-divider">|</span>
                  <button className="ctrl-btn" onClick={() => setShowBoard(true)} aria-label="View Mindmap">
                    [VIEW_MINDMAP]
                  </button>
                  <span className="ctrl-divider">|</span>
                  <button className="ctrl-btn" onClick={handleShutdown} aria-label="Exit System">
                    [EXIT_SYSTEM]
                  </button>
                </div>
              </div>

              <Terminal history={history} />

              {uiState?.choices && uiState.choices.length > 0 && (
                <ChoiceGrid
                  choices={uiState.choices}
                  handleChoice={handleSend}
                  loading={loading}
                />
              )}

              <InputConsole
                input={input}
                setInput={setInput}
                handleSend={handleSend}
                loading={loading}
              />
            </div>

            {showBoard && (
              <MindMap
                boardData={uiState?.board_data}
                onClose={() => setShowBoard(false)}
              />
            )}
          </Layout>
        </div>
      )}
    </>
  )
}

export default App
