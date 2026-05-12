import React from 'react';
import { PlusCircle } from 'lucide-react';

const agentColors = {
    orchestrator:   'text-purple-400',
    ingestion:      'text-blue-400',
    retrieval:      'text-cyan-400',
    qa:             'text-green-400',
    summarizer:     'text-yellow-400',
    translator:     'text-orange-400',
    data_extraction:'text-red-400',
    email_drafting: 'text-pink-400',
    comparison:     'text-indigo-400',
};

export default function Sidebar({ onUploadClick }) {
    return (
        <div className="flex flex-col gap-4 p-4">
            {/* Header */}
            <div className="flex items-center gap-2 px-1">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-cyan-500 flex items-center justify-center flex-shrink-0">
                    <span className="text-white font-bold text-sm">D</span>
                </div>
                <div>
                    <h1 className="text-white font-bold text-sm leading-tight">DocuAgent</h1>
                    <p className="text-white/40 text-xs">Multi-Agent AI System</p>
                </div>
            </div>

            <hr className="border-white/10" />

            {/* Upload Button */}
            <button
                onClick={onUploadClick}
                className="flex items-center gap-2 w-full px-3 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-cyan-600 text-white text-sm font-medium hover:opacity-90 transition-opacity"
            >
                <PlusCircle size={16} />
                Upload Document
            </button>

            {/* Spacer — DocumentManager renders below this in App.jsx */}
            <div className="flex-1" />

            {/* Agent Legend */}
            <div className="border-t border-white/10 pt-3">
                <p className="text-white/40 text-xs font-semibold uppercase tracking-wider px-1 mb-2">Agents</p>
                <div className="grid grid-cols-2 gap-x-2 gap-y-1">
                    {Object.entries(agentColors).map(([name, color]) => (
                        <div key={name} className="flex items-center gap-1.5">
                            <div className={`w-1.5 h-1.5 rounded-full ${color.replace('text-', 'bg-')}`} />
                            <span className="text-white/40 text-xs capitalize">{name.replace(/_/g, ' ')}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
