import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import Sidebar from './components/Sidebar.jsx';
import ChatInterface from './components/ChatInterface.jsx';
import ActivityPanel from './components/ActivityPanel.jsx';
import DocumentUpload from './components/DocumentUpload.jsx';
import DocumentManager from './components/DocumentManager.jsx';
import EmailModal from './components/EmailModal.jsx';

const API_BASE_URL = 'http://localhost:8000';

function App() {
    const [sessionId]        = useState(uuidv4);
    const [documents, setDocuments]     = useState([]);
    const [selectedDocId, setSelectedDocId] = useState(null);
    const [compareDocId, setCompareDocId]   = useState(null);
    const [messages, setMessages]           = useState([
        { role: 'assistant', content: '👋 Hello! I\'m your DocuAgent. Upload a document and start chatting — or upload two documents and ask me to compare them!' }
    ]);
    const [logs, setLogs]         = useState([]);
    const [isUploadOpen, setIsUploadOpen] = useState(false);
    const [isEmailOpen, setIsEmailOpen]   = useState(false);
    const [emailContent, setEmailContent] = useState('');
    const [isTyping, setIsTyping]         = useState(false);
    const streamingIdRef = useRef(null);

    // ── Load document list from backend on mount ──────────────────────────────
    useEffect(() => {
        axios.get(`${API_BASE_URL}/documents`)
            .then(res => setDocuments(res.data.documents || []))
            .catch(() => {/* backend might not be up yet */});
    }, []);

    // ── Streaming send (SSE) ──────────────────────────────────────────────────
    const handleSendMessage = async (content) => {
        setMessages(prev => [...prev, { role: 'user', content }]);
        setIsTyping(true);

        // Use streaming endpoint
        try {
            const response = await fetch(`${API_BASE_URL}/chat/stream`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: content,
                    session_id: sessionId,
                    namespace: selectedDocId,
                    compare_namespace: compareDocId || undefined,
                }),
            });

            if (!response.ok) {
                const err = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
                throw new Error(err.detail || 'Stream request failed');
            }

            const reader  = response.body.getReader();
            const decoder = new TextDecoder();
            let agentName  = 'qa';
            let agentReason = '';
            let buffer     = '';
            let msgId      = Date.now();
            streamingIdRef.current = msgId;

            // Add streaming placeholder message
            setIsTyping(false);
            setMessages(prev => [...prev, {
                role: 'assistant', content: '', agent: null, streaming: true, _id: msgId
            }]);

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop(); // keep incomplete line

                for (const line of lines) {
                    if (!line.startsWith('data: ')) continue;
                    const raw = line.slice(6);

                    if (raw === '[DONE]') break;

                    if (raw.startsWith('__META__')) {
                        try {
                            const meta = JSON.parse(raw.slice(8));
                            agentName   = meta.agent;
                            agentReason = meta.reasoning;
                            // Update the placeholder with agent info
                            setMessages(prev => prev.map(m =>
                                m._id === msgId ? { ...m, agent: agentName } : m
                            ));
                            setLogs(prev => [{
                                agent: 'Orchestrator',
                                action: `Routed to ${agentName}`,
                                reasoning: agentReason
                            }, ...prev]);
                        } catch { /* ignore */ }
                        continue;
                    }

                    if (raw.startsWith('__ERROR__')) {
                        setMessages(prev => prev.map(m =>
                            m._id === msgId
                                ? { ...m, content: `❌ Error: ${raw.slice(9)}`, streaming: false }
                                : m
                        ));
                        continue;
                    }

                    // Regular token — append to streaming message
                    setMessages(prev => prev.map(m =>
                        m._id === msgId
                            ? { ...m, content: m.content + raw }
                            : m
                    ));
                }
            }

            // Finalise streaming message
            setMessages(prev => prev.map(m =>
                m._id === msgId ? { ...m, streaming: false } : m
            ));

            // Open email modal if needed
            if (agentName === 'email_drafting') {
                setMessages(prev => {
                    const found = prev.find(m => m._id === msgId);
                    if (found) setEmailContent(found.content);
                    return prev;
                });
                setIsEmailOpen(true);
            }

        } catch (error) {
            setIsTyping(false);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `❌ ${error.message || 'Error processing your request.'}`
            }]);
        }
    };

    // ── Upload handler ────────────────────────────────────────────────────────
    const handleUpload = async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        try {
            const res = await axios.post(`${API_BASE_URL}/upload`, formData);
            const newDoc = {
                doc_id:      res.data.doc_id,
                doc_name:    res.data.doc_name,
                chunk_count: res.data.chunks || 0,
                uploaded_at: new Date().toISOString(),
            };
            setDocuments(prev => [newDoc, ...prev]);
            setSelectedDocId(newDoc.doc_id);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `✅ **${newDoc.doc_name}** uploaded (${newDoc.chunk_count} chunks). What would you like to do with it?`
            }]);
        } catch (error) {
            const detail = error.response?.data?.detail || error.message;
            setMessages(prev => [...prev, { role: 'assistant', content: `❌ Upload failed: ${detail}` }]);
        }
    };

    // ── Delete handler ────────────────────────────────────────────────────────
    const handleDelete = (docId) => {
        setDocuments(prev => prev.filter(d => d.doc_id !== docId));
        if (selectedDocId === docId) setSelectedDocId(null);
        if (compareDocId  === docId) setCompareDocId(null);
    };

    // ── Select / Compare ──────────────────────────────────────────────────────
    const handleSelectDoc = (docId) => {
        setSelectedDocId(docId);
        // Clear compare if switching primary
        if (compareDocId === docId) setCompareDocId(null);
    };

    const handleCompareDoc = (docId) => {
        setCompareDocId(docId);
        if (docId) {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: '⇄ Comparison mode active. Now ask me to "compare the two documents" or ask a specific comparison question.'
            }]);
        }
    };

    return (
        <div className="flex h-screen w-screen bg-background overflow-hidden text-white">
            {/* Background blobs */}
            <div className="fixed top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/20 rounded-full blur-[120px] pointer-events-none" />
            <div className="fixed bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-secondary/20 rounded-full blur-[120px] pointer-events-none" />

            {/* Sidebar with embedded DocumentManager */}
            <div className="flex flex-col w-64 flex-shrink-0 border-r border-white/10 bg-black/20 backdrop-blur-sm overflow-y-auto">
                <Sidebar
                    documents={[]}            /* handled by DocumentManager now */
                    selectedDocId={selectedDocId}
                    onUploadClick={() => setIsUploadOpen(true)}
                    onSelectDoc={handleSelectDoc}
                />
                <DocumentManager
                    documents={documents}
                    selectedDocId={selectedDocId}
                    compareDocId={compareDocId}
                    onSelectDoc={handleSelectDoc}
                    onCompareDoc={handleCompareDoc}
                    onDelete={handleDelete}
                />
            </div>

            <ChatInterface
                messages={messages}
                isTyping={isTyping}
                sessionId={sessionId}
                onSendMessage={handleSendMessage}
                onFileClick={() => setIsUploadOpen(true)}
                selectedDocId={selectedDocId}
                compareDocId={compareDocId}
                onAddLog={(log) => setLogs(prev => [log, ...prev])}
            />

            <ActivityPanel logs={logs} />

            <DocumentUpload
                isOpen={isUploadOpen}
                onClose={() => setIsUploadOpen(false)}
                onUpload={handleUpload}
            />

            <EmailModal
                isOpen={isEmailOpen}
                onClose={() => setIsEmailOpen(false)}
                content={emailContent}
            />
        </div>
    );
}

export default App;
