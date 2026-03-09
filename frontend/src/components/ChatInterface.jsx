import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Bot, User } from 'lucide-react';

const agentBadgeColors = {
    orchestrator: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
    ingestion: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
    retrieval: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
    qa: 'bg-green-500/20 text-green-300 border-green-500/30',
    summarizer: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
    translator: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
    data_extraction: 'bg-red-500/20 text-red-300 border-red-500/30',
    email_drafting: 'bg-pink-500/20 text-pink-300 border-pink-500/30',
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

function Message({ msg }) {
    const isUser = msg.role === 'user';
    const badgeClass = msg.agent ? agentBadgeColors[msg.agent] || 'bg-white/10 text-white/60 border-white/10' : null;

    return (
        <div className={`flex items-end gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${isUser ? 'bg-white/10' : 'bg-gradient-to-br from-purple-500 to-cyan-500'}`}>
                {isUser ? <User size={16} className="text-white/60" /> : <Bot size={16} className="text-white" />}
            </div>
            <div className={`max-w-[75%] flex flex-col gap-1 ${isUser ? 'items-end' : 'items-start'}`}>
                {msg.agent && (
                    <span className={`text-xs px-2 py-0.5 rounded-full border capitalize ${badgeClass}`}>
                        {msg.agent.replace('_', ' ')} agent
                    </span>
                )}
                <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${isUser
                        ? 'bg-gradient-to-br from-purple-600/80 to-cyan-600/80 text-white rounded-br-sm'
                        : 'bg-white/5 border border-white/10 text-white/90 rounded-bl-sm'
                    }`}>
                    {msg.content}
                </div>
            </div>
        </div>
    );
}

export default function ChatInterface({ messages, isTyping, onSendMessage, onFileClick }) {
    const [input, setInput] = useState('');
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

    return (
        <main className="flex-1 flex flex-col h-full overflow-hidden">
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
                        placeholder="Ask something about your documents..."
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
                <p className="text-white/20 text-xs text-center mt-2">Press Enter to send · Shift+Enter for new line</p>
            </div>
        </main>
    );
}
