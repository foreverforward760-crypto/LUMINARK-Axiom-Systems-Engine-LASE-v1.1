'use client';

import { motion } from 'framer-motion';

interface InfoButtonProps {
  content: string;
  title?: string;
}

export default function InfoButton({ content, title }: InfoButtonProps) {
  return (
    <div className="group relative inline-block">
      <button className="w-6 h-6 rounded-full border-2 border-luminark-accent text-luminark-accent flex items-center justify-center text-xs font-bold hover:bg-luminark-accent hover:text-white transition-all">
        i
      </button>
      
      {/* Tooltip */}
      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-64 p-4 bg-luminark-card border border-luminark-border rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 z-50">
        {title && (
          <h4 className="font-semibold text-luminark-accent mb-2">{title}</h4>
        )}
        <p className="text-sm text-luminark-text leading-relaxed">{content}</p>
        {/* Arrow */}
        <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
          <div className="w-3 h-3 bg-luminark-card border-b border-r border-luminark-border transform rotate-45"></div>
        </div>
      </div>
    </div>
  );
}
