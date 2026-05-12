import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Bot, User, Download, ChevronDown } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const agentBadgeColors = {
    orchestrator:   'bg-purple-500/20 text-purple-300 border-purple-500/30',
    ingestion:      'bg-blue-500/20 text-blue-300 border-blue-500/30',
    retrieval:      'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
    qa:             'bg-green-500/20 text-green-300 border-green-500/30',
    summarizer:     'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
    translator:     'bg-orange-500/20 text-orange-300 border-orange-500/30',
    data_extraction:'bg-red-500/20 text-red-300 border-red-500/30',
    email_drafting: 'bg-pink-500/20 text-pink-300 border-pink-500/30',
    comparison:     'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
};

function TypingIndicator() {
    return (
        <div className="flex items-end gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-cyan-500 flex items-center justify-center flex-shrink-0">
                <Bot size={16} className="text-white" />
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl rounded-bl-sm px-4 py-3">
                <div className="flex gap-1 items-center h-4">
                    <div className="w-2 h-2 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
            </div>
        </div>
    );
}

function StreamingCursor() {
    return <span className="inline-block w-0.5 h-4 bg-white/70 ml-0.5 animate-pulse align-middle" />;
}

function Message({ msg }) {
    const isUser = msg.role === 'user';
    const badgeClass = msg.agent
        ? agentBadgeColors[msg.agent] || 'bg-white/10 text-white/60 border-white/10'
        : null;

    return (
        <div className={`flex items-end gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                isUser ? 'bg-white/10' : 'bg-gradient-to-br from-purple-500 to-cyan-500'
            }`}>
                {isUser ? <User size={16} className="text-white/60" /> : <Bot size={16} className="text-white" />}
            </div>
            <div className={`max-w-[78%] flex flex-col gap-1 ${isUser ? 'items-end' : 'items-start'}`}>
                {msg.agent && (
                    <span className={`text-xs px-2 py-0.5 rounded-full border capitalize ${badgeClass}`}>
                        {msg.agent.replace(/_/g, ' ')} agent
                    </span>
                )}
                <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
                    isUser
                        ? 'bg-gradient-to-br from-purple-600/80 to-cyan-600/80 text-white rounded-br-sm'
                        : 'bg-white/5 border border-white/10 text-white/90 rounded-bl-sm'
                }`}>
                    {msg.content}
                    {msg.streaming && <StreamingCursor />}
                </div>
            </div>
        </div>
    );
}

export default function ChatInterface({
    messages, isTyping, sessionId,
    onSendMessage, onFileClick,
    selectedDocId, compareDocId,
    onAddLog,
}) {
    const [input, setInput] = useState('');
    const [exportOpen, setExportOpen] = useState(false);
    const bottomRef = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isTyping]);

    const handleSend = () => {
        if (!input.trim()) return;
        onSendMessage(input.trim());
        setInput('');
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleExport = async (format) => {
        setExportOpen(false);
        try {
            const res = await axios.post(
                `${API_BASE_URL}/export`,
                { session_id: sessionId, format },
                { responseType: 'blob' }
            );
            const ext = format === 'json' ? 'json' : 'md';
            const url = URL.createObjectURL(res.data);
            const a   = document.createElement('a');
            a.href     = url;
            a.download = `docuagent_chat.${ext}`;
            a.click();
            URL.revokeObjectURL(url);
        } catch (err) {
            alert(`Export failed: ${err.response?.data?.detail || err.message}`);
        }
    };

    const hasMessages = messages.some(m => m.role !== 'assistant' || m.content !== messages[0]?.content);

    return (
        <main className="flex-1 flex flex-col h-full overflow-hidden">
            {/* Toolbar */}
            <div className="flex items-center justify-between px-4 py-2 border-b border-white/10 bg-black/10">
                <div className="flex items-center gap-2 text-xs text-white/40">
                    {selectedDocId
                        ? <span className="text-purple-300">📄 Document active</span>
                        : <span>No document selected</span>
                    }
                    {compareDocId && <span className="text-cyan-300 ml-1">⇄ Comparing</span>}
                </div>

                {/* Export dropdown */}
                <div className="relative">
                    <button
                        onClick={() => setExportOpen(v => !v)}
                        className="flex items-center gap-1.5 text-xs text-white/40 hover:text-white/70 transition-colors px-2 py-1 rounded-lg hover:bg-white/5"
                    >
                        <Download size={13} />
                        Export
                        <ChevronDown size={11} />
                    </button>
                    {exportOpen && (
                        <div className="absolute right-0 top-full mt-1 z-50 bg-slate-900 border border-white/10 rounded-xl shadow-xl overflow-hidden min-w-[140px]">
                            <button onClick={() => handleExport('markdown')} className="w-full text-left px-3 py-2 text-xs text-white/80 hover:bg-white/10 transition-colors">
                                📝 Export as Markdown
                            </button>
                            <button onClick={() => handleExport('json')} className="w-full text-left px-3 py-2 text-xs text-white/80 hover:bg-white/10 transition-colors">
                                📦 Export as JSON
                            </button>
                        </div>
                    )}
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-5">
                {messages.map((msg, i) => <Message key={i} msg={msg} />)}
                {isTyping && <TypingIndicator />}
                <div ref={bottomRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-white/10 bg-black/20 backdrop-blur-sm">
                <div className="flex items-end gap-2 bg-white/5 border border-white/10 rounded-2xl px-3 py-2">
                    <button
                        onClick={onFileClick}
                        className="p-2 text-white/40 hover:text-white/80 transition-colors flex-shrink-0"
                        title="Attach document"
                    >
                        <Paperclip size={18} />
                    </button>
                    <textarea
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={
                            compareDocId
                                ? 'Ask something to compare the two selected documents...'
                                : 'Ask something about your documents...'
                        }
                        rows={1}
                        className="flex-1 bg-transparent text-white placeholder-white/30 text-sm resize-none outline-none py-1.5 max-h-40 overflow-y-auto"
                        style={{ lineHeight: '1.5' }}
                    />
                    <button
                        onClick={handleSend}
                        disabled={!input.trim()}
                        className="p-2 bg-gradient-to-br from-purple-500 to-cyan-500 rounded-xl text-white disabled:opacity-30 disabled:cursor-not-allowed hover:opacity-90 transition-opacity flex-shrink-0"
                    >
                        <Send size={16} />
                    </button>
                </div>
                <p className="text-white/20 text-xs text-center mt-2">
                    Enter to send · Shift+Enter for new line
                    {compareDocId && ' · ⇄ Comparison mode active'}
                </p>
            </div>
        </main>
    );
}
