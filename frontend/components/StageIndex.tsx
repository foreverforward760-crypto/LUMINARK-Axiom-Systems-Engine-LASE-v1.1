'use client';

import { motion } from 'framer-motion';
import { ARCHETYPAL_STAGES } from '@/data/systemData';
import InfoButton from './InfoButton';

interface StageIndexProps {
  onClose: () => void;
}

export default function StageIndex({ onClose }: StageIndexProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-luminark-card border border-luminark-border rounded-2xl p-8 max-w-4xl max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-3xl font-bold text-luminark-text mb-2">
              The 10 Archetypal Stages
            </h2>
            <p className="text-luminark-muted">
              A complete reference guide to your journey through transformation
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-luminark-muted hover:text-luminark-text text-2xl"
          >
            ×
          </button>
        </div>

        <div className="space-y-6">
          {ARCHETYPAL_STAGES.map((stage, index) => (
            <motion.div
              key={stage.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="border border-luminark-border rounded-xl p-6 hover:border-luminark-accent transition-all"
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-luminark-accent/20 rounded-full flex items-center justify-center text-luminark-accent font-mono font-bold">
                  {stage.id}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-bold text-luminark-text">
                      {stage.name}
                    </h3>
                    <span className="text-sm text-luminark-muted italic">
                      {stage.subtitle}
                    </span>
                  </div>
                  <p className="text-luminark-text mb-3 font-medium">
                    {stage.description}
                  </p>
                  <p className="text-sm text-luminark-muted leading-relaxed mb-3">
                    {stage.fullDescription}
                  </p>
                  <div className="mt-4 p-3 bg-luminark-bg/50 rounded-lg border-l-4 border-luminark-accent">
                    <p className="text-sm text-luminark-accent font-medium">
                      🎯 {stage.guidance}
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
}
