import { useState, useEffect } from 'react'
import { Terminal, Activity, Zap, Shield, HelpCircle, Play, Square, RefreshCw, ScrollText, FileText } from 'lucide-react'

// Types
type ViewState = 'home' | 'recording' | 'automation' | 'dashboard' | 'reports'
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

  const fetchSavedScripts = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/recorder/saved-scripts')
      const data = await res.json()
      setSavedScripts(data.scripts || [])
    } catch (e) {
      console.error("Failed to fetch scripts", e)
    }
  }

  const fetchReports = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/recorder/reports')
      const data = await res.json()
      setReports(data.reports || [])
    } catch (e) { console.error(e) }
  }

  const runTest = async (filename: string) => {
    setIsRunning(filename)
    try {
      await fetch(`http://localhost:8000/api/v1/recorder/run/${filename}`, { method: 'POST' })
      // Poll after 3s to see if it started
      setTimeout(fetchReports, 3000)
    } catch (e) { console.error(e) }
    finally { setIsRunning(null) }
  }

  useEffect(() => {
    fetchSavedScripts()
    fetchReports()
  }, [])

  // Polling for steps when recording
  useEffect(() => {
    let interval: any
    if (isRecording && sessionId) {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`http://localhost:8000/api/v1/recorder/${sessionId}/steps`)
          const data = await res.json()
          if (data.steps) setSteps(data.steps)
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
      const res = await fetch('http://localhost:8000/api/v1/recorder/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, session_name: 'manual-test' })
      })
      const data = await res.json()
      if (data.session_id) {
        setSessionId(data.session_id)
        setIsRecording(true)
        setView('recording')
        setCode('') // Reset code on new session
        setSteps([])
      } else {
        setError("Failed to start recording session")
      }
    } catch (e) {
      setError("Network error: Could not connect to backend")
    }
  }

  const stopRecording = async () => {
    if (!sessionId) return
    try {
      await fetch(`http://localhost:8000/api/v1/recorder/stop/${sessionId}`, { method: 'POST' })
      setIsRecording(false)
    } catch (e) {
      console.error("Failed to stop", e)
    }
  }

  const generateCode = async () => {
    if (steps.length === 0) return
    try {
      const res = await fetch(`http://localhost:8000/api/v1/recorder/custom-code?url=${encodeURIComponent(url)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ steps })
      })
      const data = await res.json()
      if (data.code) {
        setCode(data.code)
        setSavedPath(data.file_path)
        setView('automation')
      }
    } catch (e) {
      setError("Failed to generate code")
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
        </nav>
      </header>

      <main className="max-w-6xl w-full pt-24 min-h-[calc(100vh-100px)]">
        {view === 'home' && (
          <div className="space-y-12">
            <section className="text-center space-y-4 pt-10">
              <h2 className="text-5xl font-extrabold tracking-tight text-white">
                Professional <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">Agentic Playwright</span> Generation
              </h2>
              <p className="text-lg text-slate-400 max-w-2xl mx-auto">
                Record manual steps and generate high-quality, self-healing Playwright tests in minutes.
              </p>
              <div className="pt-6">
                <button
                  onClick={() => setView('recording')}
                  className="px-8 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-full font-bold transition-all shadow-lg shadow-blue-500/20"
                >
                  Start New Recording
                </button>
              </div>
            </section>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <FeatureCard
                icon={<Terminal className="w-8 h-8 text-blue-400" />}
                title="Manual Recorder"
                description="Capture every click and input with high-stability CSS selectors."
                onClick={() => setView('recording')}
              />
              <FeatureCard
                icon={<Activity className="w-8 h-8 text-emerald-400" />}
                title="AI Test Generator"
                description="Convert recordings into Playwright scripts using Smolagents and advanced LLMs."
                onClick={() => setView('automation')}
              />
              <FeatureCard
                icon={<Shield className="w-8 h-8 text-purple-400" />}
                title="Self-Healing Logic"
                description="AI Vision automatically repairs broken locators when the UI changes."
              />
              <FeatureCard
                icon={<HelpCircle className="w-8 h-8 text-orange-400" />}
                title="Burmese DSL"
                description="Native language commands for localized and intuitive automation."
              />
            </div>
          </div>
        )}

        {view === 'recording' && (
          <div className="max-w-4xl mx-auto space-y-8">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <Terminal className="text-blue-400" /> Web Recorder
              </h2>
              <div className="flex items-center gap-2">
                {isRecording ? (
                  <span className="flex items-center gap-2 text-red-400 animate-pulse text-sm font-bold uppercase tracking-wider">
                    <div className="w-2 h-2 bg-red-500 rounded-full"></div> Recording Live
                  </span>
                ) : (
                  <span className="text-slate-500 text-sm">Idle</span>
                )}
              </div>
            </div>

            <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-6">
              {!isRecording ? (
                <div className="space-y-4">
                  <label className="block text-sm font-medium text-slate-400">Target URL</label>
                  <div className="flex gap-4">
                    <input
                      type="text"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                      placeholder="https://example.com"
                    />
                    <button
                      onClick={startRecording}
                      className="flex items-center gap-2 px-6 py-3 bg-emerald-600 hover:bg-emerald-500 rounded-lg font-bold transition-colors"
                    >
                      <Play className="w-4 h-4 fill-current" /> Start
                    </button>
                  </div>
                  {error && <p className="text-red-400 text-sm">{error}</p>}
                </div>
              ) : (
                <div className="flex items-center justify-between p-4 bg-slate-950 rounded-xl border border-blue-500/30">
                  <div>
                    <p className="text-white font-medium">Recording Session: {sessionId?.substring(0, 8)}...</p>
                    <p className="text-sm text-slate-400">{url}</p>
                  </div>
                  <button
                    onClick={stopRecording}
                    className="flex items-center gap-2 px-6 py-2 bg-red-600 hover:bg-red-500 rounded-lg font-bold transition-colors"
                  >
                    <Square className="w-4 h-4 fill-current" /> Stop
                  </button>
                </div>
              )}
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-slate-300">Recorded Steps ({steps.length})</h3>
                {!isRecording && steps.length > 0 && (
                  <button
                    onClick={generateCode}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg font-bold text-sm transition-colors"
                  >
                    <Activity className="w-4 h-4" /> Generate Code
                  </button>
                )}
              </div>
              <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden min-h-[200px]">
                {steps.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-48 text-slate-500">
                    <RefreshCw className="w-8 h-8 mb-2 opacity-50" />
                    <p>Waiting for actions...</p>
                  </div>
                ) : (
                  <div className="divide-y divide-slate-800">
                    {steps.map((step, idx) => (
                      <div key={idx} className="p-4 flex items-start gap-4 hover:bg-slate-800/50 transition-colors">
                        <span className="flex items-center justify-center w-6 h-6 rounded-full bg-slate-800 text-slate-400 text-xs font-mono">
                          {idx + 1}
                        </span>
                        <div>
                          <p className="font-mono text-sm text-blue-400">{step.action_type.toUpperCase()}</p>
                          <p className="text-slate-300 text-sm break-all font-mono mt-1">{step.selector_snapshot}</p>
                          {step.input_value_masked && (
                            <p className="text-xs text-emerald-400 mt-1">Value: "{step.input_value_masked}"</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-4 pt-8 border-t border-slate-800">
              <h3 className="text-lg font-semibold text-slate-300 flex items-center gap-2">
                <ScrollText className="text-blue-400 w-5 h-5" /> Saved Scripts History
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {savedScripts.length === 0 ? (
                  <p className="text-sm text-slate-500 italic">No saved scripts yet.</p>
                ) : (
                  savedScripts.map((script: string, idx: number) => (
                    <div key={idx} className="p-3 bg-slate-900 border border-slate-800 rounded-lg hover:border-blue-500/50 transition-colors group flex items-center justify-between">
                      <div className="flex items-center gap-3 truncate">
                        <div className="p-2 bg-slate-950 rounded-md">
                          <Terminal className="w-4 h-4 text-slate-400 group-hover:text-blue-400" />
                        </div>
                        <div className="truncate">
                          <p className="text-xs font-mono text-slate-300 truncate">{script}</p>
                          <p className="text-[10px] text-slate-500">tests_web/</p>
                        </div>
                      </div>
                      <button
                        onClick={() => runTest(script)}
                        disabled={isRunning === script}
                        className={`p-2 rounded-md ${isRunning === script ? 'bg-slate-800 text-slate-600' : 'bg-blue-600/20 text-blue-400 hover:bg-blue-600 hover:text-white'} transition-all`}
                      >
                        {isRunning === script ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {view === 'automation' && (
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <Activity className="text-emerald-400" /> Generated Playwright Code
              </h2>
              {savedPath && (
                <div className="flex items-center gap-2 px-3 py-1 bg-slate-900 border border-slate-800 rounded-full text-[10px] font-mono text-slate-400">
                  <Shield className="w-3 h-3 text-blue-400" /> {savedPath}
                </div>
              )}
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 relative group">
              {code ? (
                <>
                  <pre className="font-mono text-sm text-slate-300 overflow-x-auto whitespace-pre-wrap">
                    {code}
                  </pre>
                  <button
                    onClick={() => navigator.clipboard.writeText(code)}
                    className="absolute top-4 right-4 px-3 py-1 bg-slate-800 text-xs rounded hover:bg-slate-700 transition-colors"
                  >
                    Copy
                  </button>
                </>
              ) : (
                <div className="flex flex-col items-center justify-center h-48 text-slate-500">
                  <Terminal className="w-8 h-8 mb-2" />
                  <p>No code generated yet. Record some steps first!</p>
                  <button
                    onClick={() => setView('recording')}
                    className="mt-4 text-blue-400 hover:text-blue-300 text-sm"
                  >
                    Go to Recorder
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
        {view === 'reports' && (
          <div className="max-w-4xl mx-auto space-y-6 animate-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <FileText className="text-purple-400" /> Automation Reports
              </h2>
              <button onClick={fetchReports} className="p-2 hover:bg-slate-800 rounded-full transition-colors">
                <RefreshCw className="w-4 h-4 text-slate-400" />
              </button>
            </div>

            <div className="grid grid-cols-1 gap-4">
              {reports.length === 0 ? (
                <div className="p-12 text-center bg-slate-900 border border-slate-800 rounded-2xl">
                  <Activity className="w-12 h-12 text-slate-700 mx-auto mb-4" />
                  <p className="text-slate-500">No reports found. Run a test script to generate one!</p>
                </div>
              ) : (
                reports.map((report: any, idx: number) => (
                  <div key={idx} className="p-6 bg-slate-900 border border-slate-800 rounded-2xl flex items-center justify-between hover:border-purple-500/50 transition-all group">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center">
                        <FileText className="text-purple-400 w-6 h-6" />
                      </div>
                      <div>
                        <h4 className="font-bold text-white group-hover:text-purple-400 transition-colors">{report.name}</h4>
                        <p className="text-xs text-slate-500 font-mono mt-1">
                          Generated: {new Date(report.timestamp * 1000).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <a
                      href={report.url}
                      target="_blank"
                      rel="noreferrer"
                      className="px-6 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg font-bold text-sm transition-all shadow-lg shadow-purple-900/20"
                    >
                      View Report
                    </a>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
        {view === 'dashboard' && <Dashboard />}
      </main>
    </div>
  )
}

function Dashboard() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/v1/recorder/usage')
        const stats = await res.json()
        setData(stats)
      } catch (e) {
        console.error("Stats fetch failed", e)
      } finally {
        setLoading(false)
      }
    }
    fetchStats()
    const interval = setInterval(fetchStats, 5000)
    return () => clearInterval(interval)
  }, [])

  if (loading) return <div className="flex items-center justify-center h-64 animate-pulse">Loading intelligence stats...</div>
  if (!data) return <div className="text-red-400">Failed to load monitoring data.</div>

  const usagePercent = Math.min(100, (data.usage.total_tokens / data.limits.daily_quota) * 100)
  const isOverQuota = data.usage.total_tokens >= data.limits.daily_quota

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold flex items-center gap-3">
          <Activity className="text-blue-400 w-8 h-8" /> System Monitor
        </h2>
        <div className={`px-4 py-1 rounded-full text-xs font-bold uppercase tracking-widest ${isOverQuota ? 'bg-red-500/20 text-red-400 border border-red-500/50' : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/50'}`}>
          {isOverQuota ? 'Local Fallback Active' : 'Cloud Primary Active'}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatsCard
          title="Daily Token Usage"
          value={data.usage.total_tokens.toLocaleString()}
          subValue={`Quota: ${data.limits.daily_quota.toLocaleString()}`}
          progress={usagePercent}
          color={isOverQuota ? "bg-red-500" : "bg-blue-500"}
        />
        <StatsCard
          title="Avg Latency"
          value={`${Math.round(data.usage.avg_latency_ms || 0)}ms`}
          subValue={`Threshold: ${data.limits.latency_threshold}ms`}
          trend={data.usage.avg_latency_ms > data.limits.latency_threshold ? "Warning" : "Healthy"}
        />
        <StatsCard
          title="Total Agents"
          value="3 Active"
          subValue="Planner, Coder, Reviewer"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl">
          <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
            <Zap className="text-yellow-400 w-5 h-5" /> Active Model Stack
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-slate-950 rounded-lg">
              <span className="text-slate-400 text-sm">Primary (Cloud)</span>
              <span className="font-mono text-blue-400">{data.limits.cloud_model}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-slate-950 rounded-lg">
              <span className="text-slate-400 text-sm">Fallback (Local)</span>
              <span className="font-mono text-emerald-400">{data.limits.local_model}</span>
            </div>
          </div>
        </div>

        <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl">
          <h3 className="text-lg font-bold mb-4">System Alerts</h3>
          <div className="space-y-2">
            {!isOverQuota ? (
              <div className="text-sm text-slate-400 flex items-center gap-2">
                <Shield className="text-emerald-500 w-4 h-4" /> All components are operating within normal parameters.
              </div>
            ) : (
              <div className="text-sm text-red-400 flex items-center gap-2">
                <Shield className="text-red-500 w-4 h-4" /> Cloud quota reached. Falling back to local inference.
              </div>
            )}
            <div className="text-sm text-slate-400 flex items-center gap-2">
              <Shield className="text-blue-500 w-4 h-4" /> Bi-directional latency monitoring active.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function StatsCard({ title, value, subValue, progress, color = "bg-blue-500", trend }: any) {
  return (
    <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl relative overflow-hidden">
      <h4 className="text-slate-500 text-xs font-bold uppercase tracking-widest mb-2">{title}</h4>
      <div className="text-3xl font-black text-white mb-1">{value}</div>
      <div className={`text-xs ${trend === 'Warning' ? 'text-orange-400' : 'text-slate-400'}`}>{subValue}</div>
      {progress !== undefined && (
        <div className="mt-4 h-1.5 w-full bg-slate-950 rounded-full overflow-hidden">
          <div className={`h-full ${color} transition-all duration-1000`} style={{ width: `${progress}%` }}></div>
        </div>
      )}
    </div>
  )
}

function FeatureCard({ icon, title, description, onClick }: { icon: React.ReactNode, title: string, description: string, onClick?: () => void }) {
  return (
    <div
      onClick={onClick}
      className={`p-6 rounded-2xl bg-slate-900 border border-slate-800 transition-all group ${onClick ? 'cursor-pointer hover:border-blue-500/50 hover:bg-slate-800' : ''}`}
    >
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-bold text-white mb-2 group-hover:text-blue-400 transition-colors">{title}</h3>
      <p className="text-slate-400 text-sm leading-relaxed">{description}</p>
    </div>
  )
}

export default App
