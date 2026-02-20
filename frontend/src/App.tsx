import React, { useState, useEffect } from 'react'
import { Zap, Shield, Settings, Brain } from 'lucide-react'
import SettingsPanel from './components/SettingsPanel'
import KnowledgeHub from './components/KnowledgeHub'
import RecordingView from './components/RecordingView'
import AutomationView from './components/AutomationView'
import { ReportsView, DashboardView } from './components/DashboardReportViews'
import HomeView from './components/HomeView'

// Types
type ViewState = 'home' | 'recording' | 'automation' | 'dashboard' | 'reports' | 'settings' | 'knowledge'
type RecordingStep = {
  id: string
  action_type: string
  selector_snapshot: string
  input_value_masked?: string
}

function App() {
  const [view, setView] = useState<ViewState>('home')
  const [url, setUrl] = useState('https://www.google.com')
  const [isRecording, setIsRecording] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [steps, setSteps] = useState<RecordingStep[]>([])
  const [error, setError] = useState<string | null>(null)
  const [code, setCode] = useState<string>('')
  const [savedPath, setSavedPath] = useState<string | null>(null)
  const [savedScripts, setSavedScripts] = useState<string[]>([])
  const [reports, setReports] = useState<any[]>([])
  const [isRunning, setIsRunning] = useState<string | null>(null)
  const [runHeadless, setRunHeadless] = useState(true)
  const [testType, setTestType] = useState('Normal')
  const [testPlans, setTestPlans] = useState<any[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [dashboardLoading, setDashboardLoading] = useState(true)

  const fetchSavedScripts = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/recorder/saved-scripts')
      const data = await res.json()
      setSavedScripts(data.scripts || [])
    } catch (e) {
      console.error("Failed to fetch scripts", e)
    }
  }

  const fetchReports = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/recorder/reports')
      const data = await res.json()
      setReports(data.reports || [])
    } catch (e) { console.error(e) }
  }

  const runTest = async (filename: string) => {
    setIsRunning(filename)
    try {
      await fetch(`http://127.0.0.1:8000/api/v1/recorder/run/${filename}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ headless: runHeadless, test_type: testType })
      })
      setTimeout(fetchReports, 3000)
    } catch (e) { console.error(e) }
    finally { setIsRunning(null) }
  }

  const fetchTestPlans = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/recorder/plans')
      const data = await res.json()
      setTestPlans(data.plans || [])
    } catch (e) { console.error(e) }
  }

  const fetchDashboardStats = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/recorder/usage')
      const stats = await res.json()
      setDashboardData(stats)
    } catch (e) {
      console.error(e)
    } finally {
      setDashboardLoading(false)
    }
  }

  useEffect(() => {
    fetchSavedScripts()
    fetchReports()
    fetchTestPlans()
    fetchDashboardStats()
    const dashboardInterval = setInterval(fetchDashboardStats, 5000)
    return () => clearInterval(dashboardInterval)
  }, [])

  useEffect(() => {
    let interval: any
    if (isRecording && sessionId) {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`http://127.0.0.1:8000/api/v1/recorder/${sessionId}/steps`)
          const data = await res.json()
          if (data.steps) setSteps(data.steps)
          if (data.error) {
            setError(data.error)
            setIsRecording(false)
          }
        } catch (e) {
          console.error("Failed to poll steps", e)
        }
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [isRecording, sessionId])

  const startRecording = async () => {
    try {
      setError(null)
      const res = await fetch('http://127.0.0.1:8000/api/v1/recorder/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, session_name: 'manual-test' })
      })
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}))
        throw new Error(errorData.detail || "Server error: Failed to start session")
      }
      const data = await res.json()
      if (data.session_id) {
        setSessionId(data.session_id)
        setIsRecording(true)
        setView('recording')
        setCode('')
        setSteps([])
      } else {
        setError("Failed to start recording session: Invalid session ID")
      }
    } catch (e: any) {
      setError(`Recording Error: ${e.message || "Network Failure"}`)
    }
  }

  const stopRecording = async () => {
    if (!sessionId) return
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/recorder/stop/${sessionId}`, { method: 'POST' })
      const data = await res.json()
      if (data.steps) setSteps(data.steps)
      setIsRecording(false)
    } catch (e) {
      console.error("Failed to stop", e)
    }
  }

  const [planName, setPlanName] = useState('SmokeTests')
  const [caseName, setCaseName] = useState('UntitledCase')

  const saveTestCase = async () => {
    try {
      setError(null)
      const res = await fetch('http://127.0.0.1:8000/api/v1/recorder/plans/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan_name: planName, case_name: caseName, steps })
      })
      const data = await res.json()
      if (data.status === 'success') {
        alert(`Saved Test Case: ${caseName} to Plan: ${planName}`)
        fetchTestPlans()
      }
    } catch (e) {
      setError("Failed to save test case")
    }
  }

  const generateFromPlan = async (plan: string, caseNameSelected: string) => {
    setIsGenerating(true)
    setError(null)
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/recorder/plans/${plan}/${caseNameSelected}`)
      const planData = await res.json()
      const genRes = await fetch(`http://127.0.0.1:8000/api/v1/recorder/custom-code?url=${encodeURIComponent(planData.steps[0]?.selector_snapshot || '')}&test_type=${testType}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ steps: planData.steps })
      })
      const genData = await genRes.json()
      setCode(genData.code)
      setSavedPath(genData.file_path)
      fetchSavedScripts()
      alert("Script generated and saved to tests_web/")
    } catch (e) {
      setError("Failed to generate code from plan")
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center p-8 bg-slate-950 text-slate-50">
      <header className="fixed top-0 left-0 right-0 p-6 flex justify-between items-center bg-slate-900/80 backdrop-blur-md border-b border-slate-800 z-10">
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => setView('home')}>
          <Zap className="text-yellow-400 w-6 h-6" />
          <h1 className="text-xl font-bold tracking-tight">AI-Aero-Playwright-Gen</h1>
        </div>
        <nav className="flex gap-6 text-sm font-medium text-slate-400">
          <button onClick={() => setView('dashboard')} className={`${view === 'dashboard' ? 'text-white' : 'hover:text-white'} transition-colors`}>Dashboard</button>
          <button onClick={() => setView('recording')} className={`${view === 'recording' ? 'text-white' : 'hover:text-white'} transition-colors`}>Recordings</button>
          <button onClick={() => setView('automation')} className={`${view === 'automation' ? 'text-white' : 'hover:text-white'} transition-colors`}>Automation</button>
          <button onClick={() => setView('reports')} className={`${view === 'reports' ? 'text-white' : 'hover:text-white'} transition-colors`}>Reports</button>
          <button onClick={() => setView('knowledge')} className={`${view === 'knowledge' ? 'text-white' : 'hover:text-white'} transition-colors flex items-center gap-1`}>
            <Brain className="w-4 h-4" /> Knowledge
          </button>
          <button onClick={() => setView('settings')} className={`${view === 'settings' ? 'text-white' : 'hover:text-white'} transition-colors flex items-center gap-1`}>
            <Settings className="w-4 h-4" /> Settings
          </button>
        </nav>
      </header>

      <main className="max-w-6xl w-full pt-24 min-h-[calc(100vh-100px)]">
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-2xl text-red-500 text-sm flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4" />
              <span>{error}</span>
            </div>
            <button onClick={() => setError(null)} className="text-[10px] uppercase font-bold hover:underline">Dismiss</button>
          </div>
        )}

        {view === 'home' && <HomeView setView={setView} />}

        {view === 'recording' && (
          <RecordingView
            url={url} setUrl={setUrl} isRecording={isRecording}
            startRecording={startRecording} stopRecording={stopRecording}
            planName={planName} setPlanName={setPlanName}
            caseName={caseName} setCaseName={setCaseName}
            steps={steps} setSteps={setSteps} saveTestCase={saveTestCase}
            savedScripts={savedScripts} runTest={runTest} isRunning={isRunning}
          />
        )}

        {view === 'automation' && (
          <AutomationView
            savedScripts={savedScripts} runTest={runTest} isRunning={isRunning}
            runHeadless={runHeadless} setRunHeadless={setRunHeadless}
            testType={testType} setTestType={setTestType}
            testPlans={testPlans} generateFromPlan={generateFromPlan}
            isGenerating={isGenerating} savedPath={savedPath} code={code}
          />
        )}

        {view === 'reports' && <ReportsView reports={reports} />}
        {view === 'dashboard' && <DashboardView data={dashboardData} loading={dashboardLoading} />}
        {view === 'settings' && <SettingsPanel />}
        {view === 'knowledge' && <KnowledgeHub />}
      </main>
    </div>
  )
}

export default App
