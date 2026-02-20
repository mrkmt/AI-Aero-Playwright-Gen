import React from 'react'
import { Terminal, Activity, Play, Square, RefreshCw, Zap } from 'lucide-react'

type RecordingStep = {
    id: string
    action_type: string
    selector_snapshot: string
    input_value_masked?: string
}

interface RecordingViewProps {
    url: string
    setUrl: (url: string) => void
    isRecording: boolean
    startRecording: () => void
    stopRecording: () => void
    planName: string
    setPlanName: (name: string) => void
    caseName: string
    setCaseName: (name: string) => void
    steps: RecordingStep[]
    setSteps: (steps: RecordingStep[]) => void
    saveTestCase: () => void
    savedScripts: string[]
    runTest: (script: string) => void
    isRunning: string | null
}

const RecordingView: React.FC<RecordingViewProps> = ({
    url, setUrl, isRecording, startRecording, stopRecording,
    planName, setPlanName, caseName, setCaseName,
    steps, setSteps, saveTestCase, savedScripts, runTest, isRunning
}) => {
    return (
        <div className="max-w-5xl mx-auto space-y-10">
            {/* Target URL Selector */}
            <div className="p-8 bg-slate-900 border border-slate-800 rounded-[32px] shadow-2xl relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-8 opacity-5 pointer-events-none">
                    <Activity className="w-24 h-24" />
                </div>
                <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
                    <Terminal className="text-blue-400 w-6 h-6" /> Web Recorder
                    <span className={`text-[10px] uppercase tracking-widest px-2 py-0.5 rounded-full border ${isRecording ? 'bg-red-500/10 border-red-500/50 text-red-500 animate-pulse' : 'bg-slate-800 border-slate-700 text-slate-500'}`}>
                        {isRecording ? 'Recording Live' : 'Idle'}
                    </span>
                </h2>

                <div className="space-y-4">
                    <div className="flex gap-4">
                        <div className="flex-1 bg-slate-950 p-1.5 rounded-2xl border border-slate-800 focus-within:border-blue-500/50 transition-all flex items-center pr-3">
                            <input
                                type="text"
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                placeholder="Enter Target URL to Record..."
                                className="flex-1 bg-transparent border-none outline-none px-4 py-3 text-sm font-medium"
                            />
                            <button
                                onClick={isRecording ? stopRecording : startRecording}
                                disabled={!url}
                                className={`${isRecording ? 'bg-red-600 hover:bg-red-500 shadow-red-500/20' : 'bg-green-600 hover:bg-green-500 shadow-green-500/20'} text-white px-6 py-2.5 rounded-xl font-bold transition-all flex items-center gap-2 shadow-lg disabled:opacity-50`}
                            >
                                {isRecording ? <Square className="w-4 h-4 fill-white" /> : <Play className="w-4 h-4 fill-white" />}
                                {isRecording ? 'Stop' : 'Start'}
                            </button>
                        </div>
                    </div>

                    <div className="flex items-center gap-4 px-2 py-2">
                        <div className="flex items-center gap-2">
                            <Zap className="w-3 h-3 text-yellow-400" />
                            <span className="text-[10px] text-slate-500 uppercase font-bold tracking-widest italic">Visual Recording Mode Active</span>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 pt-2">
                        <div className="space-y-1">
                            <label className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Test Plan Name</label>
                            <input
                                type="text"
                                value={planName}
                                onChange={(e) => setPlanName(e.target.value)}
                                placeholder="e.g. SmokeTests"
                                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500/30"
                            />
                        </div>
                        <div className="space-y-1">
                            <label className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Test Case Name</label>
                            <input
                                type="text"
                                value={caseName}
                                onChange={(e) => setCaseName(e.target.value)}
                                placeholder="e.g. LoginFlow"
                                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500/30"
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* Recorded Steps Table */}
            <div className="space-y-4">
                <div className="flex justify-between items-center px-4">
                    <h3 className="font-bold flex items-center gap-2">
                        Recorded Steps ({steps.length})
                    </h3>
                    <button
                        onClick={saveTestCase}
                        className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-xl text-sm font-bold flex items-center gap-2 shadow-lg shadow-blue-500/20 transition-all"
                    >
                        <RefreshCw className="w-4 h-4" /> Save Test Case
                    </button>
                </div>

                <div className="bg-slate-900/50 border border-slate-800 rounded-3xl overflow-hidden backdrop-blur-sm">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="border-b border-slate-800 bg-slate-900/80">
                                <th className="px-4 py-3 text-[10px] font-bold text-slate-500 uppercase">#</th>
                                <th className="px-4 py-3 text-[10px] font-bold text-slate-500 uppercase">Command</th>
                                <th className="px-4 py-3 text-[10px] font-bold text-slate-500 uppercase">Target (Selector)</th>
                                <th className="px-4 py-3 text-[10px] font-bold text-slate-500 uppercase">Value / Input</th>
                                <th className="px-4 py-3 text-[10px] font-bold text-slate-500 uppercase">Action</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/50">
                            {steps.map((step, idx) => (
                                <tr key={idx} className="hover:bg-slate-800/30 transition-colors group">
                                    <td className="px-4 py-3 text-xs font-mono text-slate-500">{idx + 1}</td>
                                    <td className="px-4 py-3">
                                        <select
                                            value={step.action_type || 'click'}
                                            onChange={(e) => {
                                                const newSteps = [...steps]
                                                newSteps[idx] = { ...step, action_type: e.target.value }
                                                setSteps(newSteps)
                                            }}
                                            className="bg-slate-950 border border-slate-800 rounded-lg px-2 py-1 text-[10px] font-bold text-blue-400 outline-none"
                                        >
                                            <option value="click">CLICK</option>
                                            <option value="fill">TYPE/FILL</option>
                                            <option value="goto">NAVIGATE</option>
                                        </select>
                                    </td>
                                    <td className="px-4 py-3">
                                        <input
                                            type="text"
                                            value={step.selector_snapshot}
                                            onChange={(e) => {
                                                const newSteps = [...steps]
                                                newSteps[idx] = { ...step, selector_snapshot: e.target.value }
                                                setSteps(newSteps)
                                            }}
                                            className="w-full bg-transparent border-none outline-none text-xs font-mono text-slate-300 focus:text-white"
                                            placeholder="Selector..."
                                        />
                                    </td>
                                    <td className="px-4 py-3">
                                        <input
                                            type="text"
                                            value={step.input_value_masked || ''}
                                            onChange={(e) => {
                                                const newSteps = [...steps]
                                                newSteps[idx] = { ...step, input_value_masked: e.target.value }
                                                setSteps(newSteps)
                                            }}
                                            className="w-full bg-transparent border-none outline-none text-xs font-mono text-green-400/80 focus:text-green-400"
                                            placeholder="Value (if any)..."
                                        />
                                    </td>
                                    <td className="px-4 py-3">
                                        <button
                                            onClick={() => {
                                                const newSteps = steps.filter((_, i) => i !== idx)
                                                setSteps(newSteps)
                                            }}
                                            className="text-slate-600 hover:text-red-400 p-1 opacity-0 group-hover:opacity-100 transition-all"
                                        >
                                            <Square className="w-3 h-3" />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            {steps.length === 0 && (
                                <tr>
                                    <td colSpan={5} className="px-4 py-12 text-center text-slate-500 text-sm">
                                        No steps recorded yet. Click <b>Start</b> to begin.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Existing scripts section extracted from App.tsx */}
                <div className="space-y-4 pt-8 border-t border-slate-800">
                    <h3 className="text-lg font-semibold text-slate-300 flex items-center gap-2">
                        Saved Scripts History
                    </h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {savedScripts.length === 0 ? (
                            <p className="text-sm text-slate-500 italic">No saved scripts yet.</p>
                        ) : (
                            savedScripts.map((script, idx) => (
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
        </div>
    )
}

export default RecordingView
