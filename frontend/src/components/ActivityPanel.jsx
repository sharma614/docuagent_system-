import React from 'react';
import { Activity, CheckCircle, Info } from 'lucide-react';
import { motion } from 'framer-motion';

const ActivityPanel = ({ logs }) => {
    return (
        <div className="w-80 glass h-screen flex flex-col p-6 z-10">
            <div className="flex items-center gap-2 mb-8 px-1">
                <Activity size={18} className="text-accent" />
                <h2 className="font-semibold text-lg">Agent Activity</h2>
            </div>

            <div className="flex-1 overflow-y-auto space-y-6 custom-scrollbar">
                {logs.map((log, idx) => (
                    <motion.div
                        key={idx}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="relative pl-6"
                    >
                        <div className={`absolute left-0 top-0 bottom-0 w-0.5 rounded-full ${log.agent === 'Orchestrator' ? 'bg-primary' :
                                log.agent === 'Retrieval' ? 'bg-secondary' : 'bg-accent'
                            }`} />

                        <div className="flex items-center gap-2 mb-1">
                            <span className={`text-[10px] font-bold uppercase px-1.5 py-0.5 rounded ${log.agent === 'Orchestrator' ? 'bg-primary/20 text-primary' :
                                    log.agent === 'Retrieval' ? 'bg-secondary/20 text-secondary' : 'bg-accent/20 text-accent'
                                }`}>
                                {log.agent}
                            </span>
                            <span className="text-[10px] text-white/30 italic">Just now</span>
                        </div>

                        <p className="text-xs text-white/80 font-medium mb-1">{log.action}</p>
                        {log.reasoning && (
                            <p className="text-[11px] text-white/40 leading-relaxed italic">{log.reasoning}</p>
                        )}
                    </motion.div>
                ))}

                {logs.length === 0 && (
                    <div className="text-center py-12 opacity-30">
                        <Info size={32} className="mx-auto mb-4" />
                        <p className="text-sm italic">Waiting for activity...</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ActivityPanel;
