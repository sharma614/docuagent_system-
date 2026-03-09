import React from 'react';
import { FileText, PlusCircle, ChevronRight } from 'lucide-react';

const agentColors = {
    orchestrator: 'text-purple-400',
    ingestion: 'text-blue-400',
    retrieval: 'text-cyan-400',
    qa: 'text-green-400',
    summarizer: 'text-yellow-400',
    translator: 'text-orange-400',
    data_extraction: 'text-red-400',
    email_drafting: 'text-pink-400',
};

export default function Sidebar({ documents, selectedDocId, onUploadClick, onSelectDoc }) {
    return (
        <aside className="w-64 flex-shrink-0 h-full flex flex-col border-r border-white/10 bg-black/20 backdrop-blur-sm p-4 gap-4">
            {/* Header */}
            <div className="flex items-center gap-2 px-2">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-cyan-500 flex items-center justify-center">
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

            {/* Document List */}
            <div className="flex-1 overflow-y-auto flex flex-col gap-1">
                <p className="text-white/40 text-xs font-semibold uppercase tracking-wider px-2 mb-1">
                    Documents ({documents.length})
                </p>
                {documents.length === 0 ? (
                    <div className="text-center py-8 text-white/30 text-xs px-2">
                        No documents yet. Upload one to get started.
                    </div>
                ) : (
                    documents.map(doc => (
                        <button
                            key={doc.id}
                            onClick={() => onSelectDoc(doc.id)}
                            className={`flex items-center gap-2 w-full px-3 py-2 rounded-lg text-sm text-left transition-colors ${selectedDocId === doc.id
                                    ? 'bg-white/15 text-white'
                                    : 'text-white/60 hover:bg-white/5 hover:text-white'
                                }`}
                        >
                            <FileText size={14} className="flex-shrink-0 text-cyan-400" />
                            <span className="flex-1 truncate">{doc.name}</span>
                            {selectedDocId === doc.id && <ChevronRight size={14} />}
                        </button>
                    ))
                )}
            </div>

            {/* Agent Legend */}
            <div className="border-t border-white/10 pt-3">
                <p className="text-white/40 text-xs font-semibold uppercase tracking-wider px-2 mb-2">Agents</p>
                <div className="grid grid-cols-2 gap-x-2 gap-y-1">
                    {Object.entries(agentColors).map(([name, color]) => (
                        <div key={name} className="flex items-center gap-1.5">
                            <div className={`w-1.5 h-1.5 rounded-full ${color.replace('text-', 'bg-')}`} />
                            <span className="text-white/40 text-xs capitalize">{name.replace('_', ' ')}</span>
                        </div>
                    ))}
                </div>
            </div>
        </aside>
    );
}
