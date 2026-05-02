'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ARCHETYPAL_STAGES, LIFE_VECTORS, ASSESSMENT_VECTORS } from '@/data/systemData';
import InfoButton from '@/components/InfoButton';
import StageIndex from '@/components/StageIndex';
import ProgressDashboard from '@/components/ProgressDashboard';

type Step = 'welcome' | 'temporal' | 'domains' | 'assessment' | 'journal' | 'complete';

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

export default function Home() {
  const [step, setStep] = useState<Step>('welcome');
  const [showStageIndex, setShowStageIndex] = useState(false);
  const [showProgress, setShowProgress] = useState(false);
  
  // Assessment data
  const [temporalFocus, setTemporalFocus] = useState<'past' | 'future' | null>(null);
  const [pastReflection, setPastReflection] = useState('');
  const [futureVision, setFutureVision] = useState('');
  const [selectedDomains, setSelectedDomains] = useState<string[]>([]);
  const [vectorScores, setVectorScores] = useState<Record<string, number>>({
    complexity: 5,
    stability: 5,
    tension: 5,
    adaptability: 5,
    coherence: 5,
  });
  const [journalText, setJournalText] = useState('');
  const [journalFrequency, setJournalFrequency] = useState<'weekly' | 'monthly'>('weekly');
  const [currentStage, setCurrentStage] = useState(0);
  
  // Load journal entries from localStorage
  const [journalEntries, setJournalEntries] = useState<JournalEntry[]>([]);

  useEffect(() => {
    const stored = localStorage.getItem('luminark-journal');
    if (stored) {
      const parsed = JSON.parse(stored);
      setJournalEntries(parsed.map((e: any) => ({
        ...e,
        date: new Date(e.date)
      })));
    }
  }, []);

  // Calculate stage based on vector scores
  useEffect(() => {
    const avgScore = Object.values(vectorScores).reduce((a, b) => a + b, 0) / 5;
    const calculatedStage = Math.round((avgScore / 10) * 9);
    setCurrentStage(calculatedStage);
  }, [vectorScores]);

  const toggleDomain = (domainId: string) => {
    setSelectedDomains(prev => 
      prev.includes(domainId) 
        ? prev.filter(id => id !== domainId)
        : [...prev, domainId]
    );
  };

  const saveJournalEntry = () => {
    const newEntry: JournalEntry = {
      id: Date.now().toString(),
      date: new Date(),
      stage: currentStage,
      vectors: vectorScores,
      reflections: {
        pastReflection,
        futureVision,
      },
      selectedDomains,
      journalText,
    };

    const updated = [...journalEntries, newEntry];
    setJournalEntries(updated);
    localStorage.setItem('luminark-journal', JSON.stringify(updated));
  };

  const resetAssessment = () => {
    setStep('welcome');
    setTemporalFocus(null);
    setPastReflection('');
    setFutureVision('');
    setSelectedDomains([]);
    setVectorScores({
      complexity: 5,
      stability: 5,
      tension: 5,
      adaptability: 5,
      coherence: 5,
    });
    setJournalText('');
  };

  return (
    <div className="min-h-screen p-4 md:p-8">
      {/* Header */}
      <motion.header 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-6xl mx-auto mb-8 flex justify-between items-center"
      >
        <div>
          <h1 className="text-4xl md:text-5xl font-bold text-luminark-text mb-2">
            LUMINARK
          </h1>
          <p className="text-luminark-muted font-mono text-sm">
            SYSTEM REFERENCE V2.0
          </p>
        </div>
        <div className="flex gap-4">
          <button
            onClick={() => setShowStageIndex(true)}
            className="px-4 py-2 bg-luminark-card border border-luminark-border rounded-lg text-luminark-text hover:border-luminark-accent transition-all"
          >
            📖 Stage Index
          </button>
          <button
            onClick={() => setShowProgress(true)}
            className="px-4 py-2 bg-luminark-card border border-luminark-border rounded-lg text-luminark-text hover:border-luminark-accent transition-all"
          >
            📊 Progress
          </button>
        </div>
      </motion.header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto">
        <AnimatePresence mode="wait">
          {/* Welcome Screen */}
          {step === 'welcome' && (
            <motion.div
              key="welcome"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-center space-y-8"
            >
              <motion.div
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                className="bg-luminark-card border border-luminark-border rounded-2xl p-12"
              >
                <h2 className="text-3xl font-bold text-luminark-text mb-4">
                  The Antikythera Engine
                </h2>
                <p className="text-luminark-muted text-lg mb-8 max-w-2xl mx-auto">
                  A bio-rhythmic assessment system for understanding your current position in the archetypal stages of transformation.
                </p>
                
                <div className="grid md:grid-cols-2 gap-6 mb-8 text-left">
                  <div className="bg-luminark-bg/50 rounded-xl p-6 border border-luminark-border">
                    <h3 className="text-xl font-semibold text-luminark-accent mb-3">The 5 Vectors</h3>
                    <ul className="space-y-2 text-sm text-luminark-muted">
                      <li>• System Complexity (C)</li>
                      <li>• Foundational Stability (S)</li>
                      <li>• Internal Tension (T)</li>
                      <li>• Fluid Adaptability (A)</li>
                      <li>• Pattern Coherence (H)</li>
                    </ul>
                  </div>
                  <div className="bg-luminark-bg/50 rounded-xl p-6 border border-luminark-border">
                    <h3 className="text-xl font-semibold text-luminark-accent mb-3">The 10 Stages</h3>
                    <ul className="space-y-2 text-sm text-luminark-muted">
                      <li>• 0: Plenara → 5: Threshold</li>
                      <li>• 6: Integration → 9: Release</li>
                      <li>• Each stage is a necessary phase</li>
                      <li>• The cycle repeats infinitely</li>
                    </ul>
                  </div>
                </div>

                <button
                  onClick={() => setStep('temporal')}
                  className="px-8 py-4 bg-luminark-accent text-white rounded-xl font-semibold text-lg hover:bg-luminark-accent/80 transition-all pulse-glow"
                >
                  Begin Assessment
                </button>
              </motion.div>
            </motion.div>
          )}

          {/* Temporal Sentiment Step */}
          {step === 'temporal' && (
            <motion.div
              key="temporal"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="bg-luminark-card border border-luminark-border rounded-2xl p-8"
            >
              <div className="flex items-center gap-3 mb-6">
                <h2 className="text-2xl font-bold text-luminark-text">
                  Time Orientation
                </h2>
                <InfoButton 
                  content="Understanding where your energy is focused—on healing the past or building the future—helps calibrate your assessment." 
                  title="Why This Matters"
                />
              </div>
              
              <p className="text-luminark-muted mb-8">
                Is your current focus more oriented toward processing the past or envisioning the future?
              </p>

              <div className="grid md:grid-cols-2 gap-6 mb-8">
                <button
                  onClick={() => setTemporalFocus('past')}
                  className={`p-6 rounded-xl border-2 transition-all text-left ${
                    temporalFocus === 'past'
                      ? 'border-luminark-accent bg-luminark-accent/10'
                      : 'border-luminark-border hover:border-luminark-accent/50'
                  }`}
                >
                  <div className="text-2xl mb-3">🔙</div>
                  <h3 className="text-xl font-semibold text-luminark-text mb-2">Past Focused</h3>
                  <p className="text-sm text-luminark-muted">
                    Processing experiences, healing wounds, understanding patterns from what has been.
                  </p>
                </button>

                <button
                  onClick={() => setTemporalFocus('future')}
                  className={`p-6 rounded-xl border-2 transition-all text-left ${
                    temporalFocus === 'future'
                      ? 'border-luminark-accent bg-luminark-accent/10'
                      : 'border-luminark-border hover:border-luminark-accent/50'
                  }`}
                >
                  <div className="text-2xl mb-3">🔮</div>
                  <h3 className="text-xl font-semibold text-luminark-text mb-2">Future Focused</h3>
                  <p className="text-sm text-luminark-muted">
                    Building vision, planning ahead, creating what wants to emerge.
                  </p>
                </button>
              </div>

              {temporalFocus && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="space-y-6"
                >
                  <div>
                    <label className="block text-luminark-text mb-3 font-medium">
                      {temporalFocus === 'past' 
                        ? 'Describe what from your past is calling for attention:' 
                        : 'Describe what future you\'re trying to create:'}
                    </label>
                    <textarea
                      value={temporalFocus === 'past' ? pastReflection : futureVision}
                      onChange={(e) => temporalFocus === 'past' 
                        ? setPastReflection(e.target.value)
                        : setFutureVision(e.target.value)
                      }
                      placeholder="Take your time to express what's alive in you..."
                      className="w-full h-32 px-4 py-3 bg-luminark-bg border border-luminark-border rounded-xl text-luminark-text placeholder-luminark-muted focus:border-luminark-accent focus:outline-none resize-none"
                    />
                  </div>

                  <button
                    onClick={() => setStep('domains')}
                    disabled={temporalFocus === 'past' ? !pastReflection : !futureVision}
                    className="w-full px-6 py-3 bg-luminark-accent text-white rounded-xl font-semibold hover:bg-luminark-accent/80 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Continue
                  </button>
                </motion.div>
              )}
            </motion.div>
          )}

          {/* Life Domains Step */}
          {step === 'domains' && (
            <motion.div
              key="domains"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="bg-luminark-card border border-luminark-border rounded-2xl p-8"
            >
              <div className="flex items-center gap-3 mb-6">
                <h2 className="text-2xl font-bold text-luminark-text">
                  Life Focus Areas
                </h2>
                <InfoButton 
                  content="Select one or more areas where your energy is most concentrated. This helps personalize your assessment to your current life situation." 
                  title="Multi-Selection Enabled"
                />
              </div>
              
              <p className="text-luminark-muted mb-8">
                Where is your energy most focused right now? (Select all that apply)
              </p>

              <div className="space-y-8 mb-8">
                {LIFE_VECTORS.map((category, catIndex) => (
                  <motion.div
                    key={category.category}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: catIndex * 0.1 }}
                  >
                    <div className="flex items-center gap-3 mb-4">
                      <h3 className="text-lg font-semibold text-luminark-accent">
                        {category.category}
                      </h3>
                      <InfoButton content={category.description} />
                    </div>
                    
                    <div className="grid md:grid-cols-3 gap-4">
                      {category.domains.map((domain) => (
                        <button
                          key={domain.id}
                          onClick={() => toggleDomain(domain.id)}
                          className={`p-4 rounded-xl border-2 transition-all text-left ${
                            selectedDomains.includes(domain.id)
                              ? 'border-luminark-accent bg-luminark-accent/10'
                              : 'border-luminark-border hover:border-luminark-accent/50'
                          }`}
                        >
                          <div className="flex items-start justify-between mb-2">
                            <h4 className="font-semibold text-luminark-text">
                              {domain.name}
                            </h4>
                            <InfoButton content={domain.info} />
                          </div>
                          <p className="text-xs text-luminark-muted">
                            {domain.description}
                          </p>
                        </button>
                      ))}
                    </div>
                  </motion.div>
                ))}
              </div>

              <button
                onClick={() => setStep('assessment')}
                disabled={selectedDomains.length === 0}
                className="w-full px-6 py-3 bg-luminark-accent text-white rounded-xl font-semibold hover:bg-luminark-accent/80 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Continue to Assessment ({selectedDomains.length} selected)
              </button>
            </motion.div>
          )}

          {/* Vector Assessment Step */}
          {step === 'assessment' && (
            <motion.div
              key="assessment"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="bg-luminark-card border border-luminark-border rounded-2xl p-8"
            >
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h2 className="text-2xl font-bold text-luminark-text mb-2">
                    Vector Assessment
                  </h2>
                  <p className="text-luminark-muted">
                    Rate each dimension from your current lived experience
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-sm text-luminark-muted mb-1">Current Stage</div>
                  <div className="text-4xl font-bold text-luminark-accent font-mono">
                    {currentStage}
                  </div>
                  <div className="text-xs text-luminark-muted">
                    {ARCHETYPAL_STAGES[currentStage].name}
                  </div>
                </div>
              </div>

              <div className="space-y-8 mb-8">
                {ASSESSMENT_VECTORS.map((vector, index) => (
                  <motion.div
                    key={vector.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-luminark-bg/50 rounded-xl p-6 border border-luminark-border"
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <h3 className="text-lg font-semibold text-luminark-text">
                        {vector.name}
                      </h3>
                      <InfoButton content={vector.info} title={vector.name} />
                    </div>
                    
                    <p className="text-sm text-luminark-muted mb-4">
                      {vector.description}
                    </p>

                    <div className="space-y-3">
                      <input
                        type="range"
                        min="0"
                        max="10"
                        step="0.1"
                        value={vectorScores[vector.id]}
                        onChange={(e) => setVectorScores({
                          ...vectorScores,
                          [vector.id]: parseFloat(e.target.value)
                        })}
                        className="w-full"
                      />
                      <div className="flex justify-between text-sm">
                        <span className="text-luminark-muted">{vector.lowLabel}</span>
                        <span className="text-luminark-accent font-mono font-bold">
                          {vectorScores[vector.id].toFixed(1)}
                        </span>
                        <span className="text-luminark-muted">{vector.highLabel}</span>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>

              <div className="bg-luminark-accent/10 border border-luminark-accent rounded-xl p-6 mb-6">
                <h3 className="text-xl font-semibold text-luminark-accent mb-3">
                  Stage {currentStage}: {ARCHETYPAL_STAGES[currentStage].name}
                </h3>
                <p className="text-sm text-luminark-text mb-3">
                  {ARCHETYPAL_STAGES[currentStage].fullDescription}
                </p>
                <div className="p-3 bg-luminark-bg/50 rounded-lg border-l-4 border-luminark-accent">
                  <p className="text-sm text-luminark-accent font-medium">
                    🎯 {ARCHETYPAL_STAGES[currentStage].guidance}
                  </p>
                </div>
              </div>

              <button
                onClick={() => setStep('journal')}
                className="w-full px-6 py-3 bg-luminark-accent text-white rounded-xl font-semibold hover:bg-luminark-accent/80 transition-all"
              >
                Continue to Journal
              </button>
            </motion.div>
          )}

          {/* Journal Entry Step */}
          {step === 'journal' && (
            <motion.div
              key="journal"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="bg-luminark-card border border-luminark-border rounded-2xl p-8"
            >
              <div className="flex items-center gap-3 mb-6">
                <h2 className="text-2xl font-bold text-luminark-text">
                  Journal Entry
                </h2>
                <InfoButton 
                  content="Regular journaling helps you track your movement through the stages over time. This creates a living map of your transformation journey." 
                  title="Why Journal?"
                />
              </div>
              
              <div className="bg-luminark-accent/10 border border-luminark-accent rounded-xl p-6 mb-6">
                <div className="text-center mb-4">
                  <div className="text-6xl font-bold text-luminark-accent font-mono mb-2">
                    {currentStage}
                  </div>
                  <div className="text-xl text-luminark-text font-semibold">
                    {ARCHETYPAL_STAGES[currentStage].name} - {ARCHETYPAL_STAGES[currentStage].subtitle}
                  </div>
                </div>
              </div>

              <div className="space-y-6 mb-8">
                <div>
                  <label className="block text-luminark-text mb-3 font-medium">
                    Journal Frequency
                  </label>
                  <div className="grid grid-cols-2 gap-4">
                    <button
                      onClick={() => setJournalFrequency('weekly')}
                      className={`p-4 rounded-xl border-2 transition-all ${
                        journalFrequency === 'weekly'
                          ? 'border-luminark-accent bg-luminark-accent/10'
                          : 'border-luminark-border hover:border-luminark-accent/50'
                      }`}
                    >
                      <div className="font-semibold text-luminark-text">Weekly</div>
                      <div className="text-sm text-luminark-muted">More frequent tracking</div>
                    </button>
                    <button
                      onClick={() => setJournalFrequency('monthly')}
                      className={`p-4 rounded-xl border-2 transition-all ${
                        journalFrequency === 'monthly'
                          ? 'border-luminark-accent bg-luminark-accent/10'
                          : 'border-luminark-border hover:border-luminark-accent/50'
                      }`}
                    >
                      <div className="font-semibold text-luminark-text">Monthly</div>
                      <div className="text-sm text-luminark-muted">Deeper reflections</div>
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-luminark-text mb-3 font-medium">
                    What's alive for you right now?
                  </label>
                  <textarea
                    value={journalText}
                    onChange={(e) => setJournalText(e.target.value)}
                    placeholder="Reflect on your current state, insights, challenges, or breakthroughs..."
                    className="w-full h-48 px-4 py-3 bg-luminark-bg border border-luminark-border rounded-xl text-luminark-text placeholder-luminark-muted focus:border-luminark-accent focus:outline-none resize-none"
                  />
                </div>
              </div>

              <button
                onClick={() => {
                  saveJournalEntry();
                  setStep('complete');
                }}
                disabled={!journalText}
                className="w-full px-6 py-3 bg-luminark-accent text-white rounded-xl font-semibold hover:bg-luminark-accent/80 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Save Entry & Complete
              </button>
            </motion.div>
          )}

          {/* Complete Step */}
          {step === 'complete' && (
            <motion.div
              key="complete"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="bg-luminark-card border border-luminark-border rounded-2xl p-12 text-center"
            >
              <div className="text-6xl mb-6">✨</div>
              <h2 className="text-3xl font-bold text-luminark-text mb-4">
                Assessment Complete
              </h2>
              <p className="text-luminark-muted mb-8 max-w-lg mx-auto">
                Your journey has been recorded. Continue returning to track your movement through the archetypal stages.
              </p>

              <div className="flex gap-4 justify-center">
                <button
                  onClick={() => setShowProgress(true)}
                  className="px-6 py-3 bg-luminark-accent text-white rounded-xl font-semibold hover:bg-luminark-accent/80 transition-all"
                >
                  View Progress
                </button>
                <button
                  onClick={resetAssessment}
                  className="px-6 py-3 bg-luminark-card border border-luminark-border text-luminark-text rounded-xl font-semibold hover:border-luminark-accent transition-all"
                >
                  New Assessment
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Modals */}
      <AnimatePresence>
        {showStageIndex && (
          <StageIndex onClose={() => setShowStageIndex(false)} />
        )}
        {showProgress && (
          <ProgressDashboard 
            entries={journalEntries} 
            onClose={() => setShowProgress(false)} 
          />
        )}
      </AnimatePresence>
    </div>
  );
}
