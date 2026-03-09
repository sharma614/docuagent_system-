import React, { useState } from 'react';
import { Upload, X, FileText, CheckCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const DocumentUpload = ({ isOpen, onClose, onUpload }) => {
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [done, setDone] = useState(false);

    const handleFileChange = (e) => {
        if (e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) return;

        setUploading(true);
        await onUpload(file);
        setUploading(false);
        setDone(true);
        setTimeout(() => {
            setDone(false);
            setFile(null);
            onClose();
        }, 1500);
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/60 backdrop-blur-sm">
            <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="glass-card w-full max-w-md p-8 relative"
            >
                <button onClick={onClose} className="absolute top-4 right-4 text-white/40 hover:text-white">
                    <X size={20} />
                </button>

                <h2 className="text-xl font-bold mb-6">Upload Document</h2>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="border-2 border-dashed border-white/10 rounded-2xl p-8 text-center hover:border-primary/50 transition-colors cursor-pointer relative">
                        <input
                            type="file"
                            onChange={handleFileChange}
                            className="absolute inset-0 opacity-0 cursor-pointer"
                            accept=".pdf,.docx,.txt"
                        />
                        {!file ? (
                            <>
                                <Upload size={32} className="mx-auto mb-4 text-primary" />
                                <p className="text-sm text-white/60">Drop your file here or click to browse</p>
                                <p className="text-[10px] text-white/20 mt-2">Supports PDF, DOCX, TXT</p>
                            </>
                        ) : (
                            <div className="flex items-center justify-center gap-3">
                                <FileText className="text-primary" />
                                <span className="text-sm font-medium">{file.name}</span>
                            </div>
                        )}
                    </div>

                    <button
                        type="submit"
                        disabled={!file || uploading || done}
                        className="w-full bg-primary hover:bg-primary/80 disabled:opacity-50 text-white py-3 rounded-xl font-bold transition-all flex items-center justify-center gap-2"
                    >
                        {uploading ? "Processing..." : done ? <CheckCircle size={18} /> : "Upload"}
                    </button>
                </form>
            </motion.div>
        </div>
    );
};

export default DocumentUpload;
