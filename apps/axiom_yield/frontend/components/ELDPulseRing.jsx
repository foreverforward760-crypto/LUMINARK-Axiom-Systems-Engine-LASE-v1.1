/**
 * ELDPulseRing.jsx – Live ELD Status Visual Indicator
 * Axiom Yield Broker Dashboard Component
 *
 * Renders a canvas-based pulse ring showing:
 *   - Physical stability arc (green/yellow)
 *   - Conscious stability arc (cyan/orange)
 *   - Evasive maneuver warning (dashed red pulse ring)
 *   - Current SAP stage label in center
 *
 * Props:
 *   physical   {number} 0–100 — physical HOS stability percentage
 *   conscious  {number} 0–100 — conscious/coherence stability percentage
 *   stage      {number} 0–9   — current SAP stage
 *   isEvasive  {boolean}      — true if HOS fraud signature detected
 */

import { useEffect, useRef } from 'react';

export default function ELDPulseRing({ physical, conscious, stage, isEvasive }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius  = 80;

    // ── Base ring (background track) ──────────────────────────────────────
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.strokeStyle = '#30363d';
    ctx.lineWidth   = 4;
    ctx.stroke();

    // ── Physical Stability arc (outer ring) ───────────────────────────────
    // Green = healthy (> 50%), Yellow = degraded (≤ 50%)
    const physicalEnd = (-Math.PI / 2) + ((physical / 100) * 2 * Math.PI);
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, -Math.PI / 2, physicalEnd);
    ctx.strokeStyle = physical > 50 ? '#00ff88' : '#ffd700';
    ctx.lineWidth   = 8;
    ctx.stroke();

    // ── Conscious Stability arc (inner ring) ──────────────────────────────
    // Cyan = coherent, Orange = incoherent (< 40%)
    const innerRadius   = radius - 16;
    const consciousEnd  = (-Math.PI / 2) + ((conscious / 100) * 2 * Math.PI);
    ctx.beginPath();
    ctx.arc(centerX, centerY, innerRadius, -Math.PI / 2, consciousEnd);
    ctx.strokeStyle = conscious > 40 ? '#00e5ff' : '#ff6b35';
    ctx.lineWidth   = 5;
    ctx.stroke();

    // ── Evasive Maneuver Warning (dashed outer pulse ring) ────────────────
    if (isEvasive) {
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius + 15, 0, 2 * Math.PI);
      ctx.strokeStyle = 'rgba(255, 51, 102, 0.7)';
      ctx.lineWidth   = 2;
      ctx.setLineDash([5, 5]);
      ctx.stroke();
      ctx.setLineDash([]); // reset dash
    }

    // ── Stage 8 Illusion of Permanence indicator (solid red outer ring) ───────────────
    if (stage === 8) {
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius + 8, 0, 2 * Math.PI);
      ctx.strokeStyle = 'rgba(255, 51, 102, 0.3)';
      ctx.lineWidth   = 6;
      ctx.stroke();
    }

    // ── Center text: SAP Stage label ──────────────────────────────────────
    ctx.fillStyle    = '#e6edf3';
    ctx.font         = 'bold 22px Orbitron, monospace';
    ctx.textAlign    = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(`STG ${stage}`, centerX, centerY - 8);

    // Sub-label: stage name abbreviation
    const stageNames = [
      'PLENARA', 'SPARK', 'FORGE', 'ENGINE',
      'CRUCIBLE', 'DYNAMO', 'NEXUS', 'LENS',
      'VESSEL', 'GUIDE'
    ];
    ctx.font         = '10px Rajdhani, sans-serif';
    ctx.fillStyle    = stage >= 7 ? '#ff3366' : '#8b949e';
    ctx.fillText(stageNames[stage] ?? `S${stage}`, centerX, centerY + 12);

  }, [physical, conscious, stage, isEvasive]);

  // Stage-dependent ring color for the container border
  const ringColor = stage >= 8
    ? 'border-[#ff3366]'
    : stage >= 6
    ? 'border-[#ffd700]'
    : 'border-[#30363d]';

  return (
    <div className="flex flex-col items-center gap-2">
      <div className={`rounded-full border-2 ${ringColor} p-1`}>
        <canvas
          ref={canvasRef}
          width={200}
          height={200}
          className="block"
          aria-label={`SAP Stage ${stage}${isEvasive ? ', Evasive Maneuver Detected' : ''}`}
        />
      </div>

      {/* HOS status bar */}
      <div className="w-full max-w-[200px]">
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>HOS</span>
          <span>{physical.toFixed(0)}%</span>
        </div>
        <div className="h-1.5 bg-[#30363d] rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${Math.min(100, physical)}%`,
              backgroundColor: physical > 50 ? '#00ff88' : physical > 25 ? '#ffd700' : '#ff3366',
            }}
          />
        </div>
      </div>

      {/* Evasive warning badge */}
      {isEvasive && (
        <span className="text-[#ff3366] text-xs font-bold animate-pulse tracking-wider uppercase">
          ⚠ Evasive Maneuver Detected
        </span>
      )}

      {/* Stage 8 trap warning */}
      {stage === 8 && !isEvasive && (
        <span className="text-[#ff6b35] text-xs font-semibold tracking-wide">
          Illusion of Permanence — Do Not Dispatch
        </span>
      )}
    </div>
  );
}
