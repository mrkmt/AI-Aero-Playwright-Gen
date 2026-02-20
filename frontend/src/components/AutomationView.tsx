import React, { useState, useEffect } from 'react'
import { Play, RefreshCw, ScrollText, Activity } from 'lucide-react'

interface AutomationViewProps {
    savedScripts: string[]
    runTest: (script: string) => void
    isRunning: string | null
    runHeadless: boolean
    setRunHeadless: (val: boolean) => void
    testType: string
    setTestType: (val: string) => void
    testPlans: any[]
    generateFromPlan: (plan: string, caseName: string) => void
    isGenerating: boolean
    savedPath: string | null
    code: string
}

const AutomationView: React.FC<AutomationViewProps> = ({
    savedScripts, runTest, isRunning, runHeadless, setRunHeadless,
    testType, setTestType, testPlans, generateFromPlan, isGenerating,
    savedPath, code
}) => {
    return (
        <div className="max-w-5xl mx-auto space-y-8">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Script Selection & Activity */}
                <div className="lg:col-span-1 space-y-6">
                    <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl h-[400px] flex flex-col">
                        <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                            <ScrollText className="text-blue-400 w-5 h-5" /> Automation Logs
                        </h3>
                        <div className="flex-1 overflow-y-auto space-y-2 custom-scrollbar">
                            <ActivityLogView />
                        </div>
                    </div>

                    <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
                        <h3 className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-2">Run Options</h3>

                        <div className="space-y-3">
                            <label className="flex items-center justify-between p-2 bg-slate-950 border border-slate-800 rounded-lg cursor-pointer">
                                <span className="text-xs text-slate-400 font-bold uppercase">Headless Mode</span>
                                <input
                                    type="checkbox"
                                    checked={runHeadless}
                                    onChange={(e) => setRunHeadless(e.target.checked)}
                                    className="w-4 h-4 rounded border-slate-700 bg-slate-900 text-blue-600"
                                />
                            </label>

                            <div className="space-y-1">
                                <label className="text-[10px] uppercase font-bold text-slate-500">Test Instruction Type</label>
                                <select
                                    value={testType}
                                    onChange={(e) => setTestType(e.target.value)}
                                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-blue-400 font-bold outline-none"
                                >
                                    <option value="Normal">NORMAL (LOGIN/SUCCESS)</option>
                                    <option value="Negative">NEGATIVE (FAIL/UNAUTHORIZED)</option>
                                    <option value="Sanity">SANITY (CORE FLOW)</option>
                                </select>
                            </div>
                        </div>

                        <h3 className="text-sm font-bold uppercase tracking-widest text-slate-500 mt-6 mb-4">Test Plans (Recorded)</h3>
                        <div className="space-y-4 max-h-[400px] overflow-y-auto custom-scrollbar">
                            {testPlans.map((plan, i) => (
                                <div key={i} className="space-y-2">
                                    <p className="text-[10px] font-black text-slate-600 uppercase tracking-tighter ml-1">{plan.name}</p>
                                    {plan.cases.map((c: string, j: number) => (
                                        <div key={j} className="flex flex-col gap-2 p-3 bg-slate-950 border border-slate-800 rounded-xl">
                                            <span className="text-xs font-bold text-slate-300 truncate">{c}</span>
                                            <button
                                                onClick={() => generateFromPlan(plan.name, c)}
                                                disabled={isGenerating}
                                                className="w-full py-1.5 bg-blue-600/10 border border-blue-500/30 text-blue-400 rounded-lg text-[10px] font-bold uppercase hover:bg-blue-600 hover:text-white transition-all disabled:opacity-50"
                                            >
                                                {isGenerating ? 'Generating...' : '🛠️ Generate Script'}
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            ))}
                        </div>

                        <h3 className="text-sm font-bold uppercase tracking-widest text-slate-500 mt-6 mb-4">Saved Scripts</h3>
                        <div className="space-y-2 max-h-[250px] overflow-y-auto">
                            {savedScripts.map((script, idx) => (
                                <div key={idx} className="flex justify-between items-center p-2 bg-slate-950 rounded border border-slate-800 hover:border-blue-500/50 transition-colors">
                                    <span className="text-xs font-mono text-slate-300 truncate">{script}</span>
                                    <button onClick={() => runTest(script)} disabled={isRunning === script} className="p-1 hover:text-blue-400">
                                        {isRunning === script ? <RefreshCw className="animate-spin w-4 h-4" /> : <Play className="w-4 h-4" />}
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Right Column: Code Display / Reports */}
                <div className="lg:col-span-2 space-y-6">
                    {savedPath && (
                        <div className="p-6 bg-emerald-900/20 border border-emerald-500/30 rounded-2xl">
                            <h3 className="text-emerald-400 font-bold mb-2">Code Generated Successfully</h3>
                            <p className="text-xs text-slate-400 font-mono mb-4 break-all">{savedPath}</p>
                            <button
                                onClick={() => runTest(savedPath.split('\\').pop() || '')}
                                className="bg-emerald-600 text-white px-6 py-2 rounded-xl text-sm font-bold hover:bg-emerald-500 transition-all"
                            >
                                Run Now
                            </button>
                        </div>
                    )}

                    {code ? (
                        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
                            <div className="px-6 py-3 bg-slate-800 border-b border-slate-700 flex justify-between items-center">
                                <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Generated Playwright Script</span>
                            </div>
                            <pre className="p-6 overflow-x-auto text-[13px] font-mono text-blue-300 leading-relaxed custom-scrollbar max-h-[600px]">
                                {code}
                            </pre>
                        </div>
                    ) : (
                        <div className="p-12 text-center bg-slate-900/30 border border-dashed border-slate-800 rounded-3xl">
                            <RefreshCw className="w-12 h-12 text-slate-700 mx-auto mb-4" />
                            <p className="text-slate-500">Select a script or record a new one to generate code.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

function ActivityLogView() {
    const [logs, setLogs] = useState<any[]>([])

    useEffect(() => {
        const fetchActivity = async () => {
            try {
                const res = await fetch('http://127.0.0.1:8000/api/v1/recorder/activity')
                const data = await res.json()
                setLogs(data.logs || [])
            } catch (e) { console.error(e) }
        }
        fetchActivity()
        const interval = setInterval(fetchActivity, 2000)
        return () => clearInterval(interval)
    }, [])

    const renderLogContent = (msg: string) => {
        if (msg.startsWith("Thought:")) {
            return (
                <div className="mt-2 mb-2 pl-3 border-l-2 border-slate-700 italic text-slate-500">
                    <span className="text-[9px] font-bold uppercase block mb-1 opacity-50">Brain Process</span>
                    {msg.replace("Thought:", "").trim()}
                </div>
            )
        }
        return msg
    }

    return (
        <div className="space-y-3 font-mono">
            {logs.map((log, i) => (
                <div key={i} className={`p-4 rounded-xl border transition-all animate-in fade-in slide-in-from-left-2 duration-500 ${log.level === 'error' ? 'bg-red-500/5 border-red-500/20' :
                    log.level === 'success' ? 'bg-emerald-500/5 border-emerald-500/20' :
                        'bg-slate-950 border-slate-800'
                    }`}>
                    <div className="flex justify-between items-center mb-2">
                        <div className="flex items-center gap-2">
                            <div className={`w-1.5 h-1.5 rounded-full ${log.level === 'error' ? 'bg-red-500 animate-pulse' :
                                log.level === 'success' ? 'bg-emerald-500' : 'bg-blue-500'
                                }`} />
                            <span className={`text-[10px] font-bold tracking-tighter uppercase px-2 py-0.5 rounded ${log.agent === 'ARCHITECT' ? 'bg-purple-500/20 text-purple-400' :
                                log.agent === 'CODER' ? 'bg-blue-500/20 text-blue-400' :
                                    log.agent === 'REVIEWER' ? 'bg-orange-500/20 text-orange-400' :
                                        'bg-slate-800 text-slate-400'
                                }`}>
                                {log.agent}
                            </span>
                        </div>
                        <span className="text-[9px] text-slate-600">{log.time_display}</span>
                    </div>
                    <div className="text-[12px] text-slate-300 leading-relaxed">
                        {renderLogContent(log.message)}
                    </div>
                </div>
            ))}
            {logs.length === 0 && (
                <div className="text-center py-10 text-slate-600 text-xs italic">
                    Waiting for agent activity...
                </div>
            )}
        </div>
    )
}

export default AutomationView
