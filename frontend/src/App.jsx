import { useState, useEffect } from 'react'
import { startGame, sendAction } from './api'
import Layout from './components/Layout'
import Terminal from './components/Terminal'
import InputConsole from './components/InputConsole'
import StatusHUD from './components/StatusHUD'
import ChoiceGrid from './components/ChoiceGrid'
import GlitchText from './components/GlitchText'
import BootSequence from './components/BootSequence'
import MindMap from './components/MindMap'
import './App.css'

function App() {
  const [booting, setBooting] = useState(true)
  const [history, setHistory] = useState([])
  const [uiState, setUiState] = useState(null)
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [showBoard, setShowBoard] = useState(false)

  useEffect(() => {
    initGame()
  }, [])

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

  if (booting) {
    return <BootSequence onComplete={() => setBooting(false)} />
  }

  return (
    <Layout uiState={uiState}>
      <div className="main-feed">
        <div className="header-deco">
          <GlitchText text="TYGER_TYGER_LIAR_LIAR" className="title-glitch" />
          <div className="system-status">
            SYS.ONLINE
            <span className="ctrl-divider">|</span>
            <button className="ctrl-btn" onClick={() => setShowBoard(true)}>
              [VIEW_MINDMAP]
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

      <div className="sidebar-feed">
        <StatusHUD uiState={uiState} />
      </div>

      {showBoard && (
        <MindMap
          boardData={uiState?.board_data}
          onClose={() => setShowBoard(false)}
        />
      )}
    </Layout>
  )
}

export default App
