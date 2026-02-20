import React, { useState, useEffect } from 'react';
import { Search, Brain, Book, Zap, Database } from 'lucide-react';

interface KnowledgeStats {
    total_documents: number;
    total_chunks: number;
    tag_distribution: Record<string, number>;
    available_test_types: string[];
}

interface SearchResult {
    id: string;
    title: string;
    content: string;
    tags: string[];
    score: number;
    type: string;
}

const KnowledgeHub: React.FC = () => {
    const [stats, setStats] = useState<KnowledgeStats | null>(null);
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<SearchResult[]>([]);
    const [searching, setSearching] = useState(false);
    const [trainingData, setTrainingData] = useState({ title: '', content: '', tags: '' });
    const [message, setMessage] = useState('');

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/v1/recorder/knowledge/stats');
            const data = await res.json();
            setStats(data);
        } catch (e) {
            console.error("Failed to fetch stats", e);
        }
    };

    const handleSearch = async () => {
        if (!query) return;
        setSearching(true);
        try {
            const res = await fetch(`http://localhost:8000/api/v1/recorder/knowledge/search?query=${encodeURIComponent(query)}`);
            const data = await res.json();
            setResults(data.results || []);
        } catch (e) {
            console.error("Search failed", e);
        } finally {
            setSearching(false);
        }
    };

    const handleTrain = async () => {
        if (!trainingData.content || !trainingData.title) return;
        try {
            const res = await fetch('http://localhost:8000/api/v1/recorder/knowledge/train', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ...trainingData,
                    tags: trainingData.tags.split(',').map(t => t.trim())
                })
            });
            if (res.ok) {
                setMessage('🧠 Knowledge Brain trained successfully!');
                setTrainingData({ title: '', content: '', tags: '' });
                fetchStats();
                setTimeout(() => setMessage(''), 3000);
            }
        } catch (e) {
            console.error("Training failed", e);
        }
    };

    return (
        <div className="max-w-6xl mx-auto p-8 text-white space-y-8 animate-in fade-in duration-500">
            <header className="flex justify-between items-center">
                <div>
                    <h2 className="text-4xl font-extrabold flex items-center gap-3">
                        <Brain className="w-10 h-10 text-pink-500" />
                        Knowledge <span className="text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-violet-500">Hub</span>
                    </h2>
                    <p className="text-slate-400 mt-2">Train your AI agents with best practices and successful automation patterns.</p>
                </div>
                {stats && (
                    <div className="flex gap-4">
                        <div className="bg-slate-900 border border-slate-800 p-4 rounded-2xl flex items-center gap-4">
                            <Database className="text-blue-400" />
                            <div>
                                <p className="text-xs text-slate-500">Stored Patterns</p>
                                <p className="text-xl font-bold">{stats.total_chunks}</p>
                            </div>
                        </div>
                    </div>
                )}
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Search Panel */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="relative group">
                        <input
                            type="text"
                            placeholder="Search the Brain (e.g. 'how to handle login flow')"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                            className="w-full bg-slate-900/80 border border-slate-700 p-5 pl-14 rounded-2xl outline-none focus:ring-2 focus:ring-pink-500 transition-all text-lg shadow-xl"
                        />
                        <Search className="absolute left-5 top-5 text-slate-500 group-focus-within:text-pink-500 transition-colors" />
                        <button
                            onClick={handleSearch}
                            disabled={searching}
                            className="absolute right-3 top-3 bg-pink-600 hover:bg-pink-500 px-6 py-2 rounded-xl font-bold transition-all disabled:opacity-50"
                        >
                            {searching ? '...' : 'Query Hub'}
                        </button>
                    </div>

                    <div className="space-y-4">
                        {results.length > 0 ? (
                            results.map((res) => (
                                <div key={res.id} className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl hover:border-pink-500/30 transition-all hover:translate-x-1 duration-300">
                                    <div className="flex justify-between items-start mb-3">
                                        <h4 className="font-bold text-lg text-pink-300 flex items-center gap-2">
                                            <Zap className="w-4 h-4 text-yellow-400" />
                                            {res.title}
                                        </h4>
                                        <span className="text-xs bg-slate-800 px-2 py-1 rounded text-slate-500 font-mono">
                                            Score: {(res.score * 100).toFixed(0)}%
                                        </span>
                                    </div>
                                    <pre className="text-sm text-slate-400 whitespace-pre-wrap font-sans bg-black/30 p-4 rounded-xl border border-white/5">
                                        {res.content}
                                    </pre>
                                    <div className="mt-4 flex gap-2 flex-wrap">
                                        {res.tags.map(tag => (
                                            <span key={tag} className="text-[10px] uppercase tracking-wider bg-pink-500/10 text-pink-400 px-2 py-1 rounded-full border border-pink-500/20">
                                                #{tag}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            ))
                        ) : query && !searching ? (
                            <div className="text-center py-12 text-slate-500 bg-slate-900/20 rounded-2xl border border-dashed border-slate-800">
                                <Book className="w-12 h-12 mx-auto mb-4 opacity-20" />
                                <p>No exact matches in the brain. Try training it some more!</p>
                            </div>
                        ) : null}
                    </div>
                </div>

                {/* Training Panel */}
                <div className="space-y-6">
                    <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl shadow-2xl sticky top-8">
                        <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                            🚀 Fast Training
                        </h3>
                        <div className="space-y-4">
                            <input
                                placeholder="Concept (e.g. Login logic)"
                                value={trainingData.title}
                                onChange={e => setTrainingData({ ...trainingData, title: e.target.value })}
                                className="w-full bg-slate-800 border-none p-4 rounded-xl focus:ring-2 focus:ring-violet-500 transition-all"
                            />
                            <textarea
                                placeholder="Paste best practice code or logic here..."
                                rows={6}
                                value={trainingData.content}
                                onChange={e => setTrainingData({ ...trainingData, content: e.target.value })}
                                className="w-full bg-slate-800 border-none p-4 rounded-xl focus:ring-2 focus:ring-violet-500 transition-all resize-none font-mono text-sm"
                            />
                            <input
                                placeholder="Tags (comma separated: login, playwright)"
                                value={trainingData.tags}
                                onChange={e => setTrainingData({ ...trainingData, tags: e.target.value })}
                                className="w-full bg-slate-800 border-none p-4 rounded-xl focus:ring-2 focus:ring-violet-500 transition-all"
                            />
                            <button
                                onClick={handleTrain}
                                className="w-full py-4 bg-gradient-to-r from-pink-600 to-violet-600 hover:from-pink-500 hover:to-violet-500 rounded-xl font-bold text-white shadow-lg transition-all active:scale-95"
                            >
                                Insert to Brain
                            </button>
                            {message && <p className="text-center text-sm font-bold text-green-400 animate-pulse">{message}</p>}
                        </div>

                        {stats && (
                            <div className="mt-10 pt-8 border-t border-slate-800">
                                <h4 className="text-sm font-bold text-slate-500 mb-4 tracking-widest uppercase">Popular Tags</h4>
                                <div className="flex flex-wrap gap-2">
                                    {Object.entries(stats.tag_distribution).slice(0, 10).map(([tag, count]) => (
                                        <div key={tag} className="flex items-center gap-2 bg-slate-800 px-3 py-1 rounded-lg text-xs">
                                            <span className="text-slate-300">{tag}</span>
                                            <span className="text-pink-500 font-bold">{count}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default KnowledgeHub;
