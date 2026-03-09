import React from 'react';
import { X, Copy, Download, Mail } from 'lucide-react';
import { motion } from 'framer-motion';

const EmailModal = ({ content, isOpen, onClose }) => {
    if (!isOpen) return null;

    const handleCopy = () => {
        navigator.clipboard.writeText(content);
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/60 backdrop-blur-sm">
            <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="glass-card w-full max-w-2xl p-8 relative flex flex-col max-h-[80vh]"
            >
                <button onClick={onClose} className="absolute top-4 right-4 text-white/40 hover:text-white">
                    <X size={20} />
                </button>

                <div className="flex items-center gap-2 mb-6">
                    <Mail className="text-primary" size={24} />
                    <h2 className="text-xl font-bold">Generated Email Draft</h2>
                </div>

                <div className="flex-1 overflow-y-auto bg-white/5 rounded-xl p-6 mb-6 font-mono text-sm leading-relaxed whitespace-pre-wrap text-white/80 border border-white/5">
                    {content || "No draft content generated yet."}
                </div>

                <div className="flex gap-4">
                    <button
                        onClick={handleCopy}
                        className="flex-1 flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 text-white py-3 rounded-xl font-medium transition-all"
                    >
                        <Copy size={18} />
                        Copy to Clipboard
                    </button>
                    <button className="flex-1 flex items-center justify-center gap-2 bg-primary hover:bg-primary/80 text-white py-3 rounded-xl font-medium transition-all">
                        <Download size={18} />
                        Download .txt
                    </button>
                </div>
            </motion.div>
        </div>
    );
};

export default EmailModal;
