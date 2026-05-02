'use client';

import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { format } from 'date-fns';

interface JournalEntry {
  id: string;
  date: Date;
  stage: number;
  vectors: Record<string, number>;
  reflections: {
    pastReflection: string;
    futureVision: string;
  };
  selectedDomains: string[];
  journalText: string;
}

interface ProgressDashboardProps {
  entries: JournalEntry[];
  onClose: () => void;
}

export default function ProgressDashboard({ entries, onClose }: ProgressDashboardProps) {
  // Prepare stage progression data
  const stageData = entries.map(entry => ({
    date: format(entry.date, 'MMM dd'),
    stage: entry.stage,
    fullDate: format(entry.date, 'PPP'),
  }));

  // Prepare vector data (latest entry)
  const latestEntry = entries[entries.length - 1];
  const vectorData = latestEntry ? Object.entries(latestEntry.vectors).map(([key, value]) => ({
    vector: key.toUpperCase(),
    value: value,
  })) : [];

  // Calculate statistics
  const avgStage = entries.length > 0 
    ? (entries.reduce((sum, e) => sum + e.stage, 0) / entries.length).toFixed(1)
    : 0;
  
  const stageChange = entries.length >= 2
    ? entries[entries.length - 1].stage - entries[entries.length - 2].stage
    : 0;

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
        className="bg-luminark-card border border-luminark-border rounded-2xl p-8 max-w-6xl max-h-[90vh] overflow-y-auto w-full"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex justify-between items-start mb-8">
          <div>
            <h2 className="text-3xl font-bold text-luminark-text mb-2">
              Your Journey Through the Stages
            </h2>
            <p className="text-luminark-muted">
              {entries.length} assessment{entries.length !== 1 ? 's' : ''} recorded
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-luminark-muted hover:text-luminark-text text-2xl"
          >
            ×
          </button>
        </div>

        {entries.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-luminark-muted text-lg">
              No journal entries yet. Complete your first assessment to start tracking your journey.
            </p>
          </div>
        ) : (
          <>
            {/* Statistics */}
            <div className="grid grid-cols-3 gap-6 mb-8">
              <div className="bg-luminark-bg/50 rounded-xl p-6 border border-luminark-border">
                <div className="text-luminark-muted text-sm mb-2">Total Entries</div>
                <div className="text-4xl font-bold text-luminark-accent">{entries.length}</div>
              </div>
              <div className="bg-luminark-bg/50 rounded-xl p-6 border border-luminark-border">
                <div className="text-luminark-muted text-sm mb-2">Average Stage</div>
                <div className="text-4xl font-bold text-luminark-accent">{avgStage}</div>
              </div>
              <div className="bg-luminark-bg/50 rounded-xl p-6 border border-luminark-border">
                <div className="text-luminark-muted text-sm mb-2">Recent Change</div>
                <div className={`text-4xl font-bold ${stageChange > 0 ? 'text-green-400' : stageChange < 0 ? 'text-yellow-400' : 'text-luminark-accent'}`}>
                  {stageChange > 0 ? '+' : ''}{stageChange}
                </div>
              </div>
            </div>

            {/* Stage Progression Chart */}
            <div className="mb-8">
              <h3 className="text-xl font-bold text-luminark-text mb-4">Stage Progression Over Time</h3>
              <div className="bg-luminark-bg/50 rounded-xl p-6 border border-luminark-border">
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={stageData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3f" />
                    <XAxis dataKey="date" stroke="#8080a0" />
                    <YAxis domain={[0, 9]} stroke="#8080a0" />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#15151f', 
                        border: '1px solid #2a2a3f',
                        borderRadius: '8px'
                      }}
                    />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="stage" 
                      stroke="#4a4aff" 
                      strokeWidth={3}
                      dot={{ fill: '#4a4aff', r: 6 }}
                      name="Stage"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Current Vector Status */}
            {vectorData.length > 0 && (
              <div className="mb-8">
                <h3 className="text-xl font-bold text-luminark-text mb-4">Current Vector Status</h3>
                <div className="bg-luminark-bg/50 rounded-xl p-6 border border-luminark-border">
                  <ResponsiveContainer width="100%" height={400}>
                    <RadarChart data={vectorData}>
                      <PolarGrid stroke="#2a2a3f" />
                      <PolarAngleAxis dataKey="vector" stroke="#8080a0" />
                      <PolarRadiusAxis angle={90} domain={[0, 10]} stroke="#8080a0" />
                      <Radar 
                        name="Vectors" 
                        dataKey="value" 
                        stroke="#4a4aff" 
                        fill="#4a4aff" 
                        fillOpacity={0.3}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            {/* Journal Entries Timeline */}
            <div>
              <h3 className="text-xl font-bold text-luminark-text mb-4">Journal Timeline</h3>
              <div className="space-y-4">
                {[...entries].reverse().map((entry, index) => (
                  <motion.div
                    key={entry.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="bg-luminark-bg/50 rounded-xl p-6 border border-luminark-border hover:border-luminark-accent transition-all"
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-16 h-16 bg-luminark-accent/20 rounded-full flex items-center justify-center text-luminark-accent font-mono font-bold text-xl">
                        {entry.stage}
                      </div>
                      <div className="flex-1">
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <div className="text-luminark-text font-semibold">
                              {format(entry.date, 'PPPP')}
                            </div>
                            <div className="text-sm text-luminark-muted">
                              {entry.selectedDomains.join(', ')}
                            </div>
                          </div>
                        </div>
                        <div className="text-sm text-luminark-muted mb-3 leading-relaxed">
                          {entry.journalText}
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-xs">
                          <div>
                            <div className="text-luminark-accent font-medium mb-1">Past Reflection:</div>
                            <div className="text-luminark-muted">{entry.reflections.pastReflection}</div>
                          </div>
                          <div>
                            <div className="text-luminark-accent font-medium mb-1">Future Vision:</div>
                            <div className="text-luminark-muted">{entry.reflections.futureVision}</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </>
        )}
      </motion.div>
    </motion.div>
  );
}
