import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import ActivityPanel from './components/ActivityPanel';
import DocumentUpload from './components/DocumentUpload';
import EmailModal from './components/EmailModal';

const API_BASE_URL = 'http://localhost:8000';

function App() {
    const [session_id] = useState(uuidv4());
    const [documents, setDocuments] = useState([]);
    const [selectedDocId, setSelectedDocId] = useState(null);
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'Hello! I am your DocuAgent. Upload a document to get started!' }
    ]);
    const [logs, setLogs] = useState([]);
    const [isUploadOpen, setIsUploadOpen] = useState(false);
    const [isEmailOpen, setIsEmailOpen] = useState(false);
    const [emailContent, setEmailContent] = useState('');
    const [isTyping, setIsTyping] = useState(false);

    const handleSendMessage = async (content) => {
        const userMsg = { role: 'user', content };
        setMessages(prev => [...prev, userMsg]);
        setIsTyping(true);

        try {
            const response = await axios.post(`${API_BASE_URL}/chat`, {
                message: content,
                session_id: session_id,
                namespace: selectedDocId
            });

            const { agent, answer, reasoning, logs: agentLogs } = response.data;

            setMessages(prev => [...prev, { role: 'assistant', content: answer, agent }]);
            setLogs(prev => [...agentLogs, ...prev]);

            if (agent === 'email_drafting') {
                setEmailContent(answer);
                setIsEmailOpen(true);
            }
        } catch (error) {
            console.error("Error sending message:", error);
            setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I encountered an error processing your request." }]);
        } finally {
            setIsTyping(false);
        }
    };

    const handleUpload = async (file) => {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post(`${API_BASE_URL}/upload`, formData);
            const newDoc = {
                id: response.data.doc_id,
                name: response.data.doc_name
            };
            setDocuments(prev => [...prev, newDoc]);
            setSelectedDocId(newDoc.id);

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `Successfully uploaded ${newDoc.name}. What would you like me to do with it?`
            }]);
        } catch (error) {
            console.error("Error uploading file:", error);
        }
    };

    return (
        <div className="flex h-screen w-screen bg-background overflow-hidden text-white">
            {/* Background Decorative Elements */}
            <div className="fixed top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/20 rounded-full blur-[120px] pointer-events-none" />
            <div className="fixed bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-secondary/20 rounded-full blur-[120px] pointer-events-none" />

            <Sidebar
                documents={documents}
                selectedDocId={selectedDocId}
                onUploadClick={() => setIsUploadOpen(true)}
                onSelectDoc={setSelectedDocId}
            />

            <ChatInterface
                messages={messages}
                isTyping={isTyping}
                onSendMessage={handleSendMessage}
                onFileClick={() => setIsUploadOpen(true)}
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
