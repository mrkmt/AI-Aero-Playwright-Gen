import React from 'react'
import { Terminal, Activity, Zap, Shield, HelpCircle, Brain } from 'lucide-react'

interface HomeViewProps {
    setView: (view: any) => void
}

const HomeView: React.FC<HomeViewProps> = ({ setView }) => {
    return (
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
                <FeatureCard
                    icon={<Brain className="w-8 h-8 text-pink-400" />}
                    title="Knowledge Hub"
                    description="Store and retrieve automation best practices using RAG intelligence."
                    onClick={() => setView('knowledge')}
                />
            </div>
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

export default HomeView
