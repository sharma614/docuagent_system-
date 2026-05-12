import React, { useState } from 'react';
import { FileText, Trash2, CheckCircle, Clock, Hash, ChevronDown, ChevronUp } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

function formatDate(iso) {
    if (!iso) return '—';
    return new Date(iso).toLocaleString(undefined, {
        month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}

export default function DocumentManager({ documents, selectedDocId, compareDocId, onSelectDoc, onCompareDoc, onDelete }) {
    const [deleting, setDeleting] = useState(null);
    const [expanded, setExpanded] = useState(true);

    const handleDelete = async (doc) => {
        if (!window.confirm(`Delete "${doc.doc_name}"? This cannot be undone.`)) return;
        setDeleting(doc.doc_id);
        try {
            await axios.delete(`${API_BASE_URL}/documents/${doc.doc_id}`);
            onDelete(doc.doc_id);
        } catch (err) {
            alert(`Failed to delete: ${err.response?.data?.detail || err.message}`);
        } finally {
            setDeleting(null);
        }
    };

    if (documents.length === 0) return null;

    return (
        <div className="px-3 pb-3">
            {/* Header toggle */}
            <button
                onClick={() => setExpanded(v => !v)}
                className="w-full flex items-center justify-between text-xs font-semibold text-white/40 uppercase tracking-widest mb-2 hover:text-white/60 transition-colors"
            >
                <span>Documents ({documents.length})</span>
                {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            </button>

            {expanded && (
                <div className="space-y-1.5">
                    {documents.map(doc => {
                        const isActive  = selectedDocId === doc.doc_id;
                        const isCompare = compareDocId  === doc.doc_id;
                        return (
                            <div
                                key={doc.doc_id}
                                className={`group rounded-xl border transition-all duration-150 ${
                                    isActive
                                        ? 'bg-purple-500/20 border-purple-500/40'
                                        : 'bg-white/5 border-white/10 hover:border-white/20'
                                }`}
                            >
                                {/* Main row */}
                                <button
                                    onClick={() => onSelectDoc(isActive ? null : doc.doc_id)}
                                    className="w-full flex items-start gap-2 p-2.5 text-left"
                                >
                                    <FileText size={14} className={`mt-0.5 flex-shrink-0 ${isActive ? 'text-purple-300' : 'text-white/40'}`} />
                                    <div className="flex-1 min-w-0">
                                        <p className={`text-xs font-medium truncate ${isActive ? 'text-purple-200' : 'text-white/80'}`}>
                                            {doc.doc_name}
                                        </p>
                                        <div className="flex items-center gap-2 mt-0.5 text-white/30 text-[10px]">
                                            <span className="flex items-center gap-0.5">
                                                <Clock size={9} /> {formatDate(doc.uploaded_at)}
                                            </span>
                                            {doc.chunk_count > 0 && (
                                                <span className="flex items-center gap-0.5">
                                                    <Hash size={9} /> {doc.chunk_count} chunks
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                    {isActive && <CheckCircle size={12} className="text-purple-400 flex-shrink-0 mt-0.5" />}
                                </button>

                                {/* Action row */}
                                <div className="flex items-center gap-1 px-2.5 pb-2 pt-0">
                                    {/* Compare toggle */}
                                    {!isActive && (
                                        <button
                                            onClick={() => onCompareDoc(isCompare ? null : doc.doc_id)}
                                            title="Compare with active document"
                                            className={`flex-1 text-[10px] px-2 py-1 rounded-lg border transition-colors ${
                                                isCompare
                                                    ? 'bg-cyan-500/20 border-cyan-500/40 text-cyan-300'
                                                    : 'bg-white/5 border-white/10 text-white/40 hover:text-white/70'
                                            }`}
                                        >
                                            {isCompare ? '✓ Compare' : 'Compare'}
                                        </button>
                                    )}
                                    {/* Delete */}
                                    <button
                                        onClick={() => handleDelete(doc)}
                                        disabled={deleting === doc.doc_id}
                                        title="Delete document"
                                        className="p-1 rounded-lg text-white/20 hover:text-red-400 hover:bg-red-500/10 transition-colors disabled:opacity-50"
                                    >
                                        <Trash2 size={12} />
                                    </button>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
