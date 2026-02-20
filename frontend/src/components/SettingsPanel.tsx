import React, { useState, useEffect } from 'react';

interface Profile {
    name: string;
    model: string;
    api_base: string | null;
    auth_file: string | null;
    api_key: string | null;
    context_limit?: number;
    max_tokens?: number;
    temperature?: number;
}

interface Config {
    profiles: Profile[];
    assignments: Record<string, string>;
    gateway?: {
        url: string;
        token: string;
    };
}

const SettingsPanel: React.FC = () => {
    const [config, setConfig] = useState<Config>({ profiles: [], assignments: {} });
    const [loading, setLoading] = useState(true);
    const [editingProfile, setEditingProfile] = useState<Profile | null>(null);

    useEffect(() => {
        fetchProfiles();
    }, []);

    const fetchProfiles = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/v1/recorder/profiles');
            const data = await res.json();
            setConfig(data);
            setLoading(false);
        } catch (e) {
            console.error("Failed to fetch profiles", e);
        }
    };

    const saveConfig = async (newConfig: Config) => {
        try {
            await fetch('http://localhost:8000/api/v1/recorder/profiles', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newConfig)
            });
            fetchProfiles();
        } catch (e) {
            console.error("Failed to save config", e);
        }
    };

    const updateAssignment = (agent: string, profileName: string) => {
        const newConfig = {
            ...config,
            assignments: { ...config.assignments, [agent]: profileName }
        };
        setConfig(newConfig);
        saveConfig(newConfig);
    };

    if (loading) return <div className="p-8 text-white">Loading Settings...</div>;

    return (
        <div className="p-8 max-w-4xl mx-auto text-white">
            <h2 className="text-3xl font-bold mb-8 flex items-center gap-3">
                <span className="text-blue-400">⚙️</span> AI Agent Settings
            </h2>

            {/* Agent Assignments */}
            <section className="mb-12 bg-slate-900/50 p-6 rounded-2xl border border-slate-800 shadow-xl">
                <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
                    🎯 Agent Assignments
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {['ARCHITECT', 'CODER', 'REVIEWER'].map((agent) => (
                        <div key={agent} className="space-y-2">
                            <label className="text-sm font-medium text-slate-400">{agent}</label>
                            <select
                                value={(config?.assignments && config.assignments[agent]) || ''}
                                onChange={(e) => updateAssignment(agent, e.target.value)}
                                className="w-full bg-slate-800 border-slate-700 text-white rounded-lg p-3 outline-none focus:ring-2 focus:ring-blue-500 transition-all cursor-pointer"
                            >
                                <option value="">Select Profile</option>
                                {(config?.profiles || []).map(p => (
                                    <option key={p.name} value={p.name}>{p.name}</option>
                                ))}
                            </select>
                        </div>
                    ))}
                </div>
            </section>

            {/* Aero Autonomous Gateway */}
            <section className="mb-12 bg-indigo-900/40 p-6 rounded-2xl border border-indigo-500/30 shadow-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4 opacity-10">
                    <span className="text-6xl font-bold">🚀</span>
                </div>
                <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
                    🛸 Aero Gateway (Autonomous)
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-400">Telegram Bot Token</label>
                        <input
                            type="password"
                            value={config.gateway?.token || ''}
                            onChange={(e) => {
                                const newConfig = { ...config, gateway: { ...config.gateway!, token: e.target.value } };
                                setConfig(newConfig);
                            }}
                            onBlur={() => saveConfig(config)}
                            placeholder="7590...:AAEV..."
                            className="w-full bg-slate-800 border-indigo-500/20 text-white rounded-lg p-3 outline-none focus:ring-2 focus:ring-indigo-500 transition-all font-mono text-sm"
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-400">Webhook Secret Key</label>
                        <input
                            type="text"
                            value={"aero_secure_secret_123"}
                            readOnly
                            className="w-full bg-slate-800/50 border-slate-700 text-slate-400 rounded-lg p-3 cursor-not-allowed font-mono text-sm"
                        />
                    </div>
                </div>

                <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-slate-900/80 rounded-xl border border-indigo-500/20">
                        <p className="text-xs text-indigo-300 font-bold mb-1 uppercase tracking-wider">Webhook Endpoint</p>
                        <p className="text-xs text-slate-400 font-mono break-all">https://api.ourspaceship.site/api/v1/recorder/telegram/webhook</p>
                    </div>
                    <div className="p-4 bg-slate-900/80 rounded-xl border border-indigo-500/20">
                        <p className="text-xs text-indigo-300 font-bold mb-1 uppercase tracking-wider">Gateway Status</p>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                            <span className="text-xs text-green-400 font-medium">Phase 1: Multi-Agent Proxy Active</span>
                        </div>
                    </div>
                    <div className="p-4 bg-slate-900/80 rounded-xl border border-indigo-500/20">
                        <p className="text-xs text-indigo-300 font-bold mb-1 uppercase tracking-wider">Identity</p>
                        <p className="text-xs text-slate-400">ourspaceship.site integration active</p>
                    </div>
                </div>

                <div className="mt-6 p-4 bg-indigo-500/10 border border-indigo-500/30 rounded-xl">
                    <p className="text-xs text-indigo-200">
                        <strong>Aero Gateway</strong> is now independent. Architect, Coder, and Reviewer use their own tokens.
                        Messages from Telegram are handled directly by Aero.
                    </p>
                </div>
            </section>

            {/* Profiles List */}
            <section className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 shadow-xl">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-xl font-semibold flex items-center gap-2">
                        👤 AI Profiles
                    </h3>
                    <button
                        onClick={() => setEditingProfile({ name: '', model: '', api_base: '', auth_file: '', api_key: '' })}
                        className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-bold transition-all"
                    >
                        + Add New
                    </button>
                </div>

                <div className="space-y-4">
                    {config.profiles.map((profile, i) => (
                        <div key={i} className="flex justify-between items-center bg-slate-800/50 p-4 rounded-xl border border-slate-700/50 hover:border-blue-500/30 transition-all">
                            <div>
                                <p className="font-bold text-blue-300">{profile.name}</p>
                                <p className="text-xs text-slate-400 font-mono mt-1">{profile.model}</p>
                            </div>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => setEditingProfile(profile)}
                                    className="text-slate-400 hover:text-white p-2"
                                >
                                    Edit
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            {/* Simple Modal for Editing */}
            {editingProfile && (
                <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
                    <div className="bg-slate-900 border border-slate-700 p-8 rounded-3xl w-full max-w-xl shadow-2xl">
                        <h4 className="text-2xl font-bold mb-6">Edit Profile</h4>
                        <div className="grid grid-cols-1 gap-4">
                            <input
                                placeholder="Profile Name"
                                value={editingProfile.name}
                                onChange={e => setEditingProfile({ ...editingProfile, name: e.target.value })}
                                className="bg-slate-800 border-none p-3 rounded-lg"
                            />
                            <input
                                placeholder="Model ID (e.g. openai/qwen-coder-plus)"
                                value={editingProfile.model}
                                onChange={e => setEditingProfile({ ...editingProfile, model: e.target.value })}
                                className="bg-slate-800 border-none p-3 rounded-lg"
                            />
                            <input
                                placeholder="API Base (Optional)"
                                value={editingProfile.api_base || ''}
                                onChange={e => setEditingProfile({ ...editingProfile, api_base: e.target.value })}
                                className="bg-slate-800 border-none p-3 rounded-lg"
                            />
                            <input
                                placeholder="Auth File Path (Optional)"
                                value={editingProfile.auth_file || ''}
                                onChange={e => setEditingProfile({ ...editingProfile, auth_file: e.target.value })}
                                className="bg-slate-800 border-none p-3 rounded-lg"
                            />
                            <input
                                placeholder="API Key (Optional)"
                                value={editingProfile.api_key || ''}
                                onChange={e => setEditingProfile({ ...editingProfile, api_key: e.target.value })}
                                className="bg-slate-800 border-none p-3 rounded-lg py-3"
                            />
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-1">
                                    <label className="text-xs text-slate-500">Context Limit</label>
                                    <input
                                        type="number"
                                        placeholder="32000"
                                        value={editingProfile.context_limit || ''}
                                        onChange={e => setEditingProfile({ ...editingProfile, context_limit: parseInt(e.target.value) })}
                                        className="bg-slate-800 border-none p-2 rounded-lg w-full"
                                    />
                                </div>
                                <div className="space-y-1">
                                    <label className="text-xs text-slate-500">Max Tokens</label>
                                    <input
                                        type="number"
                                        placeholder="4096"
                                        value={editingProfile.max_tokens || ''}
                                        onChange={e => setEditingProfile({ ...editingProfile, max_tokens: parseInt(e.target.value) })}
                                        className="bg-slate-800 border-none p-2 rounded-lg w-full"
                                    />
                                </div>
                            </div>
                        </div>
                        <div className="flex justify-end gap-3 mt-8">
                            <button
                                onClick={() => setEditingProfile(null)}
                                className="px-6 py-2 rounded-xl text-slate-400 hover:bg-slate-800 font-bold"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={() => {
                                    const index = config.profiles.findIndex(p => p.name === editingProfile.name);
                                    const newProfiles = [...config.profiles];
                                    if (index > -1) newProfiles[index] = editingProfile;
                                    else newProfiles.push(editingProfile);
                                    const newConfig = { ...config, profiles: newProfiles };
                                    setConfig(newConfig);
                                    saveConfig(newConfig);
                                    setEditingProfile(null);
                                }}
                                className="bg-blue-600 px-8 py-2 rounded-xl text-white font-bold hover:bg-blue-500 shadow-lg shadow-blue-500/20"
                            >
                                Save Profile
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SettingsPanel;
