import React from 'react'
import { FileText, Zap } from 'lucide-react'

interface ReportsViewProps {
    reports: any[]
}

export const ReportsView: React.FC<ReportsViewProps> = ({ reports }) => {
    return (
        <div className="max-w-5xl mx-auto space-y-8">
            <h2 className="text-3xl font-bold flex items-center gap-3">
                <FileText className="text-purple-400" /> Execution Reports
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {reports.map((r, i) => (
                    <a key={i} href={r.url} target="_blank" rel="noreferrer" className="p-4 bg-slate-900 border border-slate-800 rounded-2xl hover:border-purple-500/50 transition-all group">
                        <div className="flex justify-between items-center">
                            <div>
                                <p className="font-bold text-slate-200 group-hover:text-purple-400 transition-colors truncate max-w-[200px]">{r.name}</p>
                                <p className="text-[10px] text-slate-500 mt-1">{new Date(r.timestamp * 1000).toLocaleString()}</p>
                            </div>
                            <div className="p-2 bg-slate-950 rounded-lg group-hover:bg-purple-600/20">
                                <FileText className="w-5 h-5 text-slate-600 group-hover:text-purple-400" />
                            </div>
                        </div>
                    </a>
                ))}
            </div>
        </div>
    )
}

interface DashboardViewProps {
    data: any
    loading: boolean
}

export const DashboardView: React.FC<DashboardViewProps> = ({ data, loading }) => {
    if (loading) return <div className="flex items-center justify-center h-64 animate-pulse">Loading intelligence...</div>
    if (!data) return <div className="text-red-400">System metrics unavailable.</div>

    const isOverQuota = data.usage.total_tokens >= data.limits.daily_quota

    return (
        <div className="max-w-5xl mx-auto space-y-8">
            <div className="flex items-center justify-between">
                <h2 className="text-3xl font-bold">System Status</h2>
                <div className={`px-4 py-1 rounded-full text-xs font-bold uppercase tracking-widest ${isOverQuota ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                    {isOverQuota ? 'Local Fallback' : 'Cloud Hybrid'}
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <StatsCard title="Tokens Today" value={data.usage.total_tokens.toLocaleString()} subValue={`Quota: ${data.limits.daily_quota}`} progress={(data.usage.total_tokens / data.limits.daily_quota) * 100} />
                <StatsCard title="Avg Latency" value={`${Math.round(data.usage.avg_latency_ms)}ms`} subValue="Limit: 15s" />
                <StatsCard title="Active Agents" value="3 Ready" subValue="Planner, Coder, Reviewer" />
            </div>

            <div className="p-8 bg-slate-900 border border-slate-800 rounded-3xl">
                <h3 className="text-xl font-bold mb-6 flex items-center gap-2"><Zap className="text-yellow-400" /> Active Infrastructure</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="p-4 bg-slate-950 rounded-2xl border border-slate-800">
                        <p className="text-[10px] uppercase font-bold text-slate-500 mb-2">Cloud Layer</p>
                        <p className="font-mono text-sm text-blue-400">{data.limits.cloud_model}</p>
                    </div>
                    <div className="p-4 bg-slate-950 rounded-2xl border border-slate-800">
                        <p className="text-[10px] uppercase font-bold text-slate-500 mb-2">Local Layer</p>
                        <p className="font-mono text-sm text-emerald-400">{data.limits.local_model}</p>
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
