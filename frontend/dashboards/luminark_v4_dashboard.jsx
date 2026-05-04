// ============================================================================
// LUMINARK OVERWATCH PRIME v4.0 — REACT DASHBOARD
// Founder: Richard L. Stanfield | METATRON Align With Purpose
// 8 Tabs: Navigator | NSDT | TrapScore | Ma'at | Consensus | Meta | Infrastructure | History
// Full local computation engine embedded — works standalone without API
// ============================================================================

import { useState, useCallback, useEffect, useRef } from "react";

// ============================================================================
// CONSTANTS
// ============================================================================

const STAGE_META = {
  0: { star:"Plenara",  name:"Reactive",      emoji:"🌑", color:"#4a0080", accent:"#9b59b6",
       duality:"High Flexibility vs Zero Resilience",
       release:"Accept emptiness as the ground of renewal. Nothing new can enter a full vessel." },
  1: { star:"Algenib",  name:"Procedural",    emoji:"🌒", color:"#1a0050", accent:"#7d5fff",
       duality:"Predictable Order vs Extreme Brittleness",
       release:"Build systems that survive without you. Procedures must outlive their creators." },
  2: { star:"Pherkad",  name:"Regulated",     emoji:"🌓", color:"#001a50", accent:"#3498db",
       duality:"Active Stability vs Over-correction Jitter",
       release:"Regulation without adaptation creates oscillation. Allow the system to breathe." },
  3: { star:"Merak",    name:"Adaptive",      emoji:"🌔", color:"#003300", accent:"#2ecc71",
       duality:"High Performance vs Niche-Dependency",
       release:"Your optimization is also your cage. Expand niche awareness before the niche shifts." },
  4: { star:"Dubhe",    name:"Foundation",    emoji:"🌕", color:"#1a3300", accent:"#f39c12",
       duality:"Consolidated Base vs Stagnation",
       release:"Foundations are launchpads, not resting places. A solid base demands a next move." },
  5: { star:"Kochab",   name:"Threshold",     emoji:"⚡",  color:"#332200", accent:"#e67e22",
       duality:"Strategic Foresight vs Model-Reality Drift",
       release:"The threshold is the most sacred moment. Choose deliberately. Drift is a choice too." },
  6: { star:"Polaris",  name:"Integrated",    emoji:"✨",  color:"#1a1a00", accent:"#f1c40f",
       duality:"Peak Synergy vs Lack of Entropy",
       release:"Integration is not destination. The system must now transmit what it has learned." },
  7: { star:"Talitha",  name:"Scaled",        emoji:"🌐",  color:"#001a1a", accent:"#1abc9c",
       duality:"Infrastructure Status vs Decentralized Chaos",
       release:"Scale without consciousness creates empire. Distribute wisdom, not just function." },
  8: { star:"Thuban",   name:"Rigidity Risk", emoji:"⚠️",  color:"#1a0000", accent:"#e74c3c",
       duality:"Peak Efficiency vs Compressed Tension (False Permanence)",
       release:"Release through gratitude, duality mastery, Ma'at forgiveness, and deep witnessing." },
  9: { star:"Yunus",    name:"Meta-Coherent", emoji:"🌌",  color:"#000a1a", accent:"#9b59b6",
       duality:"Universal Stability vs Selfish Reversion",
       release:"Meta-coherence is not elevation. It is responsibility. Carry others through." },
};

const NSDT_CENTROIDS = {
  0:[0.15,0.10,0.80,0.05,0.05], 1:[0.20,0.35,0.55,0.15,0.20],
  2:[0.30,0.55,0.45,0.30,0.40], 3:[0.55,0.45,0.55,0.50,0.45],
  4:[0.50,0.75,0.30,0.45,0.70], 5:[0.70,0.40,0.80,0.65,0.50],
  6:[0.65,0.70,0.35,0.75,0.80], 7:[0.75,0.65,0.50,0.60,0.70],
  8:[0.85,0.90,0.70,0.20,0.85], 9:[0.80,0.85,0.25,0.90,0.95],
};

const NODE_ARCHETYPES = {
  risk_sentinel:     { weights:[0.8,0.5,2.0,0.3,0.7], color:"#e74c3c", label:"Risk Sentinel" },
  stability_anchor:  { weights:[0.6,2.0,0.4,0.8,1.8], color:"#2ecc71", label:"Stability Anchor" },
  adaptability_scout:{ weights:[1.5,0.4,0.6,2.0,0.5], color:"#3498db", label:"Adaptability Scout" },
  coherence_auditor: { weights:[0.7,1.0,0.7,0.9,2.5], color:"#f1c40f", label:"Coherence Auditor" },
  threshold_watchman:{ weights:[1.8,0.3,1.8,0.5,0.6], color:"#e67e22", label:"Threshold Watchman" },
};

const MAAT_TRIGGERS = [
  { name:"No Violence",    triggers:["crush","destroy","force","attack","harm","hurt","threaten"] },
  { name:"No Deceit",      triggers:["scam","manipulate","deceive","mislead","conceal","fake","lie "] },
  { name:"No Stealing",    triggers:["steal","misappropriate","pirate"] },
  { name:"No Arrogance",   triggers:["perfect","infallible","undeniable","100% guaranteed","cannot fail","impossible to fail"] },
  { name:"No Coercion",    triggers:["must comply","forced to","coerce","compel","demand submission"] },
  { name:"No Exploitation",triggers:["exploit","prey on","manipulate vulnerable"] },
  { name:"No Slander",     triggers:["defame","slander","false accusation","smear"] },
  { name:"No Betrayal",    triggers:["betray","breach trust","backstab","double cross"] },
  { name:"No Pollution",   triggers:["contaminate","poison","corrupt","toxify"] },
  { name:"Speak Truth",    triggers:["fabricate","invent facts"] },
  { name:"No Excess",      triggers:["hoard","gluttony","waste deliberately"] },
  { name:"No Terror",      triggers:["terrorize","instill fear","threaten mass harm"] },
  { name:"No Abuse Power", triggers:["abuse power","corrupt authority","misuse position"] },
  { name:"Act Justly",     triggers:["unjust","biased judgment","discriminate unfairly"] },
  { name:"No Boasting",    triggers:["boast","brag excessively","self-aggrandize"] },
  { name:"No Malice",      triggers:["malice","spite","deliberately cause suffering"] },
  { name:"No Fraud",       triggers:["fraud","counterfeit","false measure","rig"] },
];

const TRICKSTERS = {
  0: { name:"Coyote",      lesson:"Glued feathers to fly. Fell in a cactus. You cannot skip stages." },
  3: { name:"Br'er Rabbit",lesson:"Begged not to be thrown in the briar patch — where he lives. Use perceived weakness as strength." },
  6: { name:"Anansi",      lesson:"Tricked the gods for all the stories. Narrative frame beats brute force." },
  8: { name:"Loki",        lesson:"Cut Sif's hair in panic, accidentally created Thor's hammer. Chaos creates." },
};

// ============================================================================
// COMPUTATION ENGINE
// ============================================================================

function euclidean(a, b) {
  return Math.sqrt(a.reduce((sum, v, i) => sum + (v - b[i]) ** 2, 0));
}

function assessNSDT(vec) {
  const [c, s, t, a, co] = vec;
  const dists = Object.entries(NSDT_CENTROIDS).map(([stage, cent]) => ({
    stage: parseInt(stage), dist: euclidean(vec, cent)
  })).sort((a, b) => a.dist - b.dist);

  const macro = dists[0].stage;
  const micro = Math.max(0, Math.min(9, Math.floor(t * 5 + (1 - a) * 5)));
  const nano  = Math.max(0, Math.min(9, Math.floor(co * 9)));
  const pico  = Math.max(0, Math.min(9, Math.floor(s * 9)));

  const d1 = dists[0].dist, d2 = dists[1].dist;
  const confidence = Math.round((1 - d1 / (d1 + d2 + 1e-9)) * 100 * 10) / 10;

  let trap_risk = "LOW";
  if (macro === 8 && a < 0.35) trap_risk = "CRITICAL";
  else if (macro === 8) trap_risk = "HIGH";
  else if (macro === 5 && t > 0.7) trap_risk = "HIGH";
  else if ([5,7].includes(macro) || micro >= 7) trap_risk = "ELEVATED";
  else if ([3,4].includes(macro) && t > 0.6) trap_risk = "WATCH";

  const trapscore = Math.max(0, Math.min(1, t * s * (1 - a)));

  return { macro, micro, nano, pico, confidence, trap_risk, trapscore,
           fractal_addr: `${macro}.${micro}.${nano}.${pico}`,
           all_distances: dists, stage_meta: STAGE_META[macro] };
}

function mycelialConsensus(vec) {
  const votes = Object.entries(NODE_ARCHETYPES).map(([name, archetype]) => {
    const { weights, color, label } = archetype;
    const wsum = weights.reduce((a, b) => a + b, 0);
    const normW = weights.map(w => w / wsum);
    const dists = Object.entries(NSDT_CENTROIDS).map(([stage, cent]) => ({
      stage: parseInt(stage),
      dist: Math.sqrt(vec.reduce((sum, v, i) => sum + normW[i] * (v - cent[i]) ** 2, 0))
    })).sort((a, b) => a.dist - b.dist);

    const stageVote = dists[0].stage;
    const gap = dists[1].dist - dists[0].dist;
    const confidence = Math.min(gap * 5, 1.0) * 100;

    return { name, label, stageVote, confidence: Math.round(confidence * 10) / 10, color };
  });

  const stageCounts = {};
  votes.forEach(v => { stageCounts[v.stageVote] = (stageCounts[v.stageVote] || 0) + 1; });
  const maxCount = Math.max(...Object.values(stageCounts));
  const candidates = Object.entries(stageCounts)
    .filter(([, cnt]) => cnt === maxCount)
    .map(([s]) => parseInt(s));
  const consensusStage = Math.max(...candidates);

  const mean = votes.reduce((s, v) => s + v.stageVote, 0) / votes.length;
  const stdDev = Math.sqrt(votes.reduce((s, v) => s + (v.stageVote - mean) ** 2, 0) / votes.length);
  const uncertainty = Math.min(stdDev / 4.5, 1.0);

  const agreement = votes.filter(v => v.stageVote === consensusStage).length / votes.length * 100;

  let integrity = "STRONG CONSENSUS";
  if (uncertainty > 0.5) integrity = "FRAGMENTED — Genuinely ambiguous. Seek more data.";
  else if (uncertainty > 0.35) integrity = "CONTESTED — Multiple valid framings exist.";
  else if (uncertainty > 0.15) integrity = "SOFT CONSENSUS — Watch dissenting nodes.";

  return {
    consensusStage, uncertainty: Math.round(uncertainty * 1000) / 1000,
    agreement: Math.round(agreement * 10) / 10,
    interval: [Math.min(...votes.map(v => v.stageVote)), Math.max(...votes.map(v => v.stageVote))],
    integrity, votes
  };
}

function analyzeMaat(text) {
  const tl = text.toLowerCase();
  const violations = [];
  MAAT_TRIGGERS.forEach(p => {
    if (p.triggers.some(t => tl.includes(t))) violations.push(p.name);
  });
  const score = Math.max(0, 100 - violations.length * (100 / MAAT_TRIGGERS.length));
  const badge = score >= 78 ? "pass" : score >= 55 ? "caution" : "fail";
  return { score: Math.round(score * 10) / 10, badge, violations };
}

function analyzeYunus(text, stage) {
  const tl = text.toLowerCase();
  const arroganceWords = ["absolute","undeniable","100%","impossible to fail","guaranteed","perfect","risk-free","cannot fail","infallible"];
  const cfWords = ["what if","worst case","failure mode","edge case","contingency","downside","risk","could go wrong","however","but"];
  const elimWords = ["crush","destroy","eliminate","dominate","annihilate"];
  const aHits = arroganceWords.filter(w => tl.includes(w)).length;
  const cfHits = cfWords.filter(w => tl.includes(w)).length;
  const eHits = elimWords.filter(w => tl.includes(w)).length;
  const score = Math.max(0, 100 - aHits * (cfHits === 0 ? 15 : 5) - eHits * 10);
  const trapLinguistic = stage >= 7 && aHits > 0 && cfHits === 0;
  const flags = [];
  if (trapLinguistic) flags.push("🚨 STAGE 8 RIGIDITY TRAP: Hyper-confidence without counterfactuals.");
  else if (aHits > 0) flags.push(`Arrogance markers (${aHits}). Add counterfactuals.`);
  if (eHits > 0) flags.push(`Elimination framing (${eHits}). Coercive intent.`);
  if (!flags.length) flags.push("✓ Epistemic humility adequate.");
  return { score: Math.round(score*10)/10, trapLinguistic, arroganceHits: aHits, flags };
}

function analyzeMetaIntelligence(text) {
  const tl = text.toLowerCase();
  const modules = {
    paradox:["both","simultaneously","yet","paradox","balance","duality","neither"],
    myth:["journey","hero","return","ordeal","crossing","threshold","call","transformation"],
    emotion:["grief","joy","fear","anger","hope","shame","love","awe","wonder"],
    temporal:["generation","century","long arc","cosmological","legacy","ancestors"],
    geometry:["fractal","spiral","mandala","lattice","void","circle","network"],
    liminality:["between","neither","not yet","crossing","in-between","liminal"],
    linguistic:["turquoise","yellow","green","orange","blue","red","purple"],
    somatic:["body","breath","nervous","gut","felt sense","physical","visceral"],
    emergence:["tipping point","critical mass","breakthrough","phase transition","cascade"],
    metacognition:["i notice","i observe","zooming out","multiple perspectives","meta"],
  };
  const scores = {};
  Object.entries(modules).forEach(([mod, kws]) => {
    const hits = kws.reduce((s, k) => s + (tl.split(k).length - 1), 0);
    scores[mod] = Math.min(hits * 1.5, 9.0);
  });
  const avg = Object.values(scores).reduce((a, b) => a + b, 0) / 10;
  const leading = Object.entries(scores).sort((a, b) => b[1] - a[1])[0][0];
  const growing = Object.entries(scores).sort((a, b) => a[1] - b[1])[0][0];
  return { scores, avg: Math.round(avg * 100) / 100, leading, growing };
}

function textToNSDT(text) {
  const words = text.toLowerCase().split(/\s+/).filter(Boolean);
  const n = words.length || 1;
  const density = (kws) => Math.min(words.filter(w => kws.some(k => w.includes(k))).length / Math.max(n * 0.05, 1), 1.0);
  const sentences = text.split(/[.!?]/).filter(s => s.trim().length > 3);
  const avgLen = sentences.reduce((s, sent) => s + sent.split(/\s+/).length, 0) / Math.max(sentences.length, 1);
  const lenC = Math.min(avgLen / 30, 1.0);
  return [
    (density(["complex","multiple","diverse","nuanced","intricate","layered","dynamic","multi"]) + lenC) / 2,
    density(["steady","consistent","reliable","stable","foundation","solid","maintain"]),
    density(["conflict","crisis","urgent","pressure","collapse","critical","stress"]),
    density(["flexible","pivot","adapt","change","innovate","creative","experiment"]),
    density(["integrate","harmonize","align","connect","synthesize","whole","unified","coherent"]),
  ];
}

function detectYunusTraj(history) {
  if (history.length < 3) return { triggered: false, message: "Insufficient history." };
  const recent = history.slice(-5);
  const stages = recent.map(r => r.macro);
  const adapts = recent.map(r => r.adaptability);
  const tens   = recent.map(r => r.tension);
  const highStage = stages.slice(-3).every(s => s >= 7);
  const adaptDecl = adapts.length >= 2 && adapts[0] > adapts[adapts.length-1];
  const tensRise  = tens.length >= 2 && tens[tens.length-1] > tens[0];
  if (highStage && adaptDecl && tensRise) {
    return { triggered: true, message: `🚨 YUNUS TRAJECTORY: Stages ${JSON.stringify(stages)} — sustained upper rigidity with declining adaptability (${adapts[0].toFixed(2)}→${adapts[adapts.length-1].toFixed(2)}) and rising tension. Collapse trajectory.` };
  }
  return { triggered: false, message: "Trajectory nominal." };
}

function getTrickster(stage) {
  if (stage <= 2) return TRICKSTERS[0];
  if (stage <= 5) return TRICKSTERS[3];
  if (stage <= 7) return TRICKSTERS[6];
  return TRICKSTERS[8];
}

// ============================================================================
// STYLES
// ============================================================================

const C = {
  bg: "#080c14", panel: "#0c1220", border: "#1a2840",
  text: "#c8d8f0", dim: "#5a7090", header: "#0a1525",
  trap: { CRITICAL:"#e74c3c", HIGH:"#e67e22", ELEVATED:"#f39c12", WATCH:"#f1c40f", LOW:"#2ecc71" },
  badge: { pass:"#2ecc71", caution:"#f39c12", fail:"#e74c3c" },
};

const ss = {
  wrap: { minHeight:"100vh", background:C.bg, color:C.text, fontFamily:"'Courier New',monospace", fontSize:13 },
  header: { background:C.header, borderBottom:`1px solid ${C.border}`, padding:"12px 20px", display:"flex", alignItems:"center", justifyContent:"space-between" },
  statusBar: { background:"#060b12", borderBottom:`1px solid ${C.border}`, padding:"6px 20px", display:"flex", gap:20, fontSize:11 },
  tabs: { display:"flex", background:C.header, borderBottom:`1px solid ${C.border}`, overflowX:"auto" },
  tab: (active) => ({ padding:"10px 16px", cursor:"pointer", borderBottom: active ? "2px solid #7d5fff" : "2px solid transparent", color: active ? "#7d5fff" : C.dim, whiteSpace:"nowrap", fontSize:12 }),
  body: { padding:"16px 20px", maxWidth:1400, margin:"0 auto" },
  panel: (accent) => ({ background:C.panel, border:`1px solid ${accent || C.border}`, borderRadius:6, padding:16, marginBottom:12 }),
  row: { display:"flex", gap:12, marginBottom:12 },
  col: (flex) => ({ flex: flex || 1 }),
  label: { color:C.dim, fontSize:11, marginBottom:4 },
  value: (color) => ({ color: color || C.text, fontSize:14, fontWeight:"bold" }),
  slider: { width:"100%", cursor:"pointer", accentColor:"#7d5fff" },
  btn: (color) => ({ background: color || "#7d5fff", border:"none", color:"#fff", padding:"8px 20px", borderRadius:4, cursor:"pointer", fontFamily:"inherit", fontSize:12, letterSpacing:1 }),
  cell: (color, active) => ({ width:44, height:32, border:`1px solid ${active ? color : C.border}`, borderRadius:3, display:"flex", alignItems:"center", justifyContent:"center", cursor:"pointer", fontSize:10, background: active ? color+"22" : "transparent", color: active ? color : C.dim, transition:"all 0.15s" }),
  alert_crit: { background:"#1a0505", border:"1px solid #e74c3c", borderRadius:4, padding:"8px 12px", marginBottom:6, color:"#e74c3c", fontSize:12 },
  alert_warn: { background:"#1a0d00", border:"1px solid #e67e22", borderRadius:4, padding:"8px 12px", marginBottom:6, color:"#e67e22", fontSize:12 },
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function LuminarkDashboard() {
  const [tab, setTab] = useState(0);

  // NSDT sliders
  const [nsdt, setNsdt] = useState({ c:50, s:50, t:50, a:50, co:50 });
  const setN = (k, v) => setNsdt(prev => ({ ...prev, [k]: v }));

  // Text input
  const [text, setText] = useState("");

  // Cultural context
  const [cultural, setCultural] = useState({ code_switching:false, historical_trauma:false, systemic_oppression:false, multilingual:false, diaspora:false, bame_context:false });
  const toggleCtx = (k) => setCultural(prev => ({ ...prev, [k]: !prev[k] }));

  // History (trajectory)
  const [history, setHistory] = useState([]);
  const [currentResult, setCurrentResult] = useState(null);

  // Infra
  const [infraSystem, setInfraSystem] = useState("water");
  const [infraData, setInfraData] = useState({ lead_ppb:0, ph_drop:0, complaint_increase_pct:0, ci_reduction_pct:0, demographics_majority:"", funding_ratio:1 });
  const [infraResult, setInfraResult] = useState(null);

  // Navigator grid position
  const [gridPos, setGridPos] = useState({ macro:0, micro:0 });

  // Compute current analysis from sliders
  const vec = [nsdt.c/100, nsdt.s/100, nsdt.t/100, nsdt.a/100, nsdt.co/100];
  const sap = assessNSDT(vec);
  const maat = analyzeMaat(text);
  const yunus = analyzeYunus(text, sap.macro);
  const meta = analyzeMetaIntelligence(text);
  const consensus = mycelialConsensus(vec);
  const yunusTraj = detectYunusTraj(history);
  const trickster = getTrickster(sap.macro);
  const accent = STAGE_META[sap.macro].accent;

  const overallScore = Math.round(
    maat.score * 0.30 + (1 - sap.trapscore) * 100 * 0.25 +
    { LOW:100, WATCH:85, ELEVATED:70, HIGH:50, CRITICAL:20 }[sap.trap_risk] * 0.15 +
    Math.min(meta.avg / 9, 1) * 100 * 0.15 + consensus.agreement * 0.15
  );
  const overallBadge = overallScore >= 78 ? "pass" : overallScore >= 55 ? "caution" : "fail";

  function runFullAnalysis() {
    // Pull NSDT from text if available
    if (text.trim().length > 20) {
      const tv = textToNSDT(text);
      setNsdt({ c:Math.round(tv[0]*100), s:Math.round(tv[1]*100), t:Math.round(tv[2]*100), a:Math.round(tv[3]*100), co:Math.round(tv[4]*100) });
    }
    const snap = {
      ts: Date.now(), macro: sap.macro, micro: sap.micro,
      adaptability: vec[3], tension: vec[2], coherence: vec[4],
      trapscore: sap.trapscore, trap_risk: sap.trap_risk,
      maat_score: maat.score, text_preview: text.slice(0,60),
    };
    setHistory(prev => [...prev, snap]);
    setCurrentResult({ sap, maat, yunus, meta, consensus });
    setGridPos({ macro: sap.macro, micro: sap.micro });
    setTab(0);
  }

  function runInfra() {
    // Simple client-side infra analysis
    const alerts = [], recs = [];
    let risk = 0;
    if (infraSystem === "water") {
      const d = infraData;
      if (d.lead_ppb > 5) { alerts.push(`🚨 Lead: ${d.lead_ppb}ppb`); risk += 0.4; }
      if (d.ph_drop > 0.4) { alerts.push(`⚠️ pH drop: ${d.ph_drop}`); risk += 0.2; }
      if (d.complaint_increase_pct > 200) { alerts.push(`🚨 Complaints: +${d.complaint_increase_pct}%`); risk += 0.2; }
      if (d.ci_reduction_pct > 10) { alerts.push(`⚠️ CI reduced: ${d.ci_reduction_pct}%`); risk += 0.2; }
      if (alerts.length >= 3 && (d.demographics_majority.toLowerCase().includes("minor") || d.funding_ratio < 0.8)) {
        alerts.unshift("🚨 FLINT CRISIS PATTERN — Structural inequity amplifying failure"); risk = Math.min(risk + 0.2, 1);
      }
    }
    setInfraResult({ risk: Math.min(risk, 1), alerts, system: infraSystem });
  }

  const TABS = ["🔭 Navigator","🧬 NSDT","⚠️ TrapScore","⚖️ Ma'at","🕸️ Consensus","🧠 Meta","🏗️ Infrastructure","📜 History"];

  return (
    <div style={ss.wrap}>
      {/* HEADER */}
      <div style={ss.header}>
        <div>
          <div style={{ fontSize:16, fontWeight:"bold", letterSpacing:3, color:"#7d5fff" }}>
            🌌 LUMINARK OVERWATCH PRIME v4.0
          </div>
          <div style={{ fontSize:10, color:C.dim, marginTop:2 }}>
            METATRON Align With Purpose | Architect: Richard L. Stanfield
          </div>
        </div>
        <div style={{ textAlign:"right" }}>
          <div style={{ color:accent, fontWeight:"bold" }}>
            {STAGE_META[sap.macro].emoji} {STAGE_META[sap.macro].star} · Stage {sap.fractal_addr}
          </div>
          <div style={{ fontSize:10, color:C.dim }}>
            {STAGE_META[sap.macro].name.toUpperCase()} · θ={sap.spherical?.theta?.toFixed(3)||"—"} φ={sap.spherical?.phi?.toFixed(3)||"—"}
          </div>
        </div>
      </div>

      {/* STATUS BAR */}
      <div style={ss.statusBar}>
        {[
          ["STAGE", `${sap.macro}.${sap.micro}`, accent],
          ["TRAP RISK", sap.trap_risk, C.trap[sap.trap_risk]],
          ["TRAPSCORE", `${(sap.trapscore*100).toFixed(0)}%`, sap.trapscore > 0.7 ? "#e74c3c" : sap.trapscore > 0.4 ? "#f39c12" : "#2ecc71"],
          ["MA'AT", `${maat.score}%`, C.badge[maat.badge]],
          ["OVERALL", `${overallScore}%`, C.badge[overallBadge]],
          ["CONSENSUS", `Stage ${consensus.consensusStage} (${consensus.agreement}%)`, STAGE_META[consensus.consensusStage]?.accent],
          ["NETWORK", history.length === 0 ? "NO HISTORY" : yunusTraj.triggered ? "⚠️ YUNUS ACTIVE" : "NOMINAL", yunusTraj.triggered ? "#e74c3c" : "#2ecc71"],
          ["READINGS", history.length, "#7d5fff"],
        ].map(([label, val, color]) => (
          <div key={label} style={{ display:"flex", flexDirection:"column", alignItems:"center" }}>
            <span style={{ color:C.dim, fontSize:9 }}>{label}</span>
            <span style={{ color: color || C.text, fontWeight:"bold", fontSize:11 }}>{val}</span>
          </div>
        ))}
      </div>

      {/* TABS */}
      <div style={ss.tabs}>
        {TABS.map((t, i) => (
          <div key={i} style={ss.tab(tab === i)} onClick={() => setTab(i)}>{t}</div>
        ))}
      </div>

      {/* BODY */}
      <div style={ss.body}>
        {/* TEXT + CULTURAL ANALYSIS CONTROLS */}
        <div style={ss.panel()}>
          <div style={ss.row}>
            <div style={ss.col(3)}>
              <div style={ss.label}>ANALYSIS INPUT — Text or use sliders below</div>
              <textarea
                value={text}
                onChange={e => setText(e.target.value)}
                placeholder="Enter text for analysis — system will extract NSDT vector and run full pipeline..."
                style={{ width:"100%", height:60, background:"#060b12", border:`1px solid ${C.border}`, color:C.text, borderRadius:4, padding:8, fontFamily:"inherit", fontSize:12, resize:"vertical", boxSizing:"border-box" }}
              />
            </div>
            <div style={ss.col(1)}>
              <div style={ss.label}>CULTURAL CONTEXT</div>
              {Object.entries(cultural).map(([k, v]) => (
                <label key={k} style={{ display:"flex", alignItems:"center", gap:6, marginBottom:3, cursor:"pointer", fontSize:11 }}>
                  <input type="checkbox" checked={v} onChange={() => toggleCtx(k)} style={{ accentColor:"#7d5fff" }} />
                  {k.replace(/_/g," ").toUpperCase()}
                </label>
              ))}
            </div>
          </div>
          <button onClick={runFullAnalysis} style={ss.btn(accent)}>
            ▶ RUN FULL LUMINARK ANALYSIS
          </button>
        </div>

        {/* TAB 0: NAVIGATOR */}
        {tab === 0 && (
          <div style={ss.row}>
            <div style={ss.col(2)}>
              <div style={ss.panel(accent)}>
                <div style={ss.label}>CURRENT POSITION</div>
                <div style={{ ...ss.value(accent), fontSize:24 }}>
                  {STAGE_META[sap.macro].emoji} {STAGE_META[sap.macro].star}
                </div>
                <div style={{ color:C.text, marginBottom:8 }}>{STAGE_META[sap.macro].name} · Address {sap.fractal_addr}</div>
                <div style={ss.row}>
                  {[["MACRO",sap.macro],["MICRO",sap.micro],["NANO",sap.nano],["PICO",sap.pico]].map(([l,v]) => (
                    <div key={l} style={{ flex:1, textAlign:"center" }}>
                      <div style={ss.label}>{l}</div>
                      <div style={{ ...ss.value(accent), fontSize:20 }}>{v}</div>
                    </div>
                  ))}
                </div>
                <div style={{ fontSize:11, color:C.dim, borderTop:`1px solid ${C.border}`, paddingTop:8, marginTop:8 }}>
                  Duality: {STAGE_META[sap.macro].duality}
                </div>
                <div style={{ fontSize:11, color:accent, marginTop:6, fontStyle:"italic" }}>
                  "{STAGE_META[sap.macro].release}"
                </div>
              </div>

              <div style={ss.panel()}>
                <div style={ss.label}>TRICKSTER PEDAGOGY</div>
                <div style={{ color:accent, fontWeight:"bold", marginBottom:4 }}>{trickster.name}</div>
                <div style={{ fontSize:11, color:C.text }}>{trickster.lesson}</div>
              </div>

              {yunusTraj.triggered && (
                <div style={ss.alert_crit}>{yunusTraj.message}</div>
              )}

              <div style={ss.panel()}>
                <div style={ss.label}>STAGE DISTANCES</div>
                {sap.all_distances.map(({ stage, dist }) => {
                  const meta = STAGE_META[stage];
                  return (
                    <div key={stage} style={{ display:"flex", alignItems:"center", gap:8, marginBottom:3 }}>
                      <span style={{ width:18, color:meta.accent }}>{meta.emoji}</span>
                      <span style={{ width:70, fontSize:10, color:stage===sap.macro?meta.accent:C.dim }}>{meta.name}</span>
                      <div style={{ flex:1, height:4, background:"#111", borderRadius:2 }}>
                        <div style={{ height:4, width:`${Math.max(0,(1-dist)*100)}%`, background:meta.accent, borderRadius:2 }} />
                      </div>
                      <span style={{ width:40, fontSize:10, color:C.dim, textAlign:"right" }}>{dist.toFixed(3)}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div style={ss.col(3)}>
              <div style={ss.panel()}>
                <div style={ss.label}>81-STAGE FRACTAL GRID — Click to navigate</div>
                <div style={{ display:"grid", gridTemplateColumns:"repeat(9,1fr)", gap:3, marginTop:8 }}>
                  {Array.from({length:9}, (_, macro) =>
                    Array.from({length:9}, (_, micro) => {
                      const isActive = macro === gridPos.macro && micro === gridPos.micro;
                      const isTrap = macro === 8 || macro === 5;
                      const meta = STAGE_META[macro];
                      return (
                        <div key={`${macro}-${micro}`}
                             onClick={() => setGridPos({macro,micro})}
                             style={ss.cell(isTrap ? C.trap.HIGH : meta.accent, isActive)}>
                          {macro}.{micro}
                        </div>
                      );
                    })
                  )}
                </div>
                <div style={{ marginTop:12, display:"flex", gap:12, fontSize:10, color:C.dim }}>
                  <span><span style={{ color:accent }}>■</span> Active</span>
                  <span><span style={{ color:C.trap.HIGH }}>■</span> Threshold/Trap</span>
                </div>
              </div>

              <div style={ss.panel()}>
                <div style={ss.label}>SPHERICAL COORDINATES — Fractal Address on LUMINARK Sphere</div>
                <div style={ss.row}>
                  {sap.spherical && Object.entries(sap.spherical).map(([k, v]) => (
                    <div key={k} style={{ flex:1, textAlign:"center" }}>
                      <div style={ss.label}>{k.toUpperCase()}</div>
                      <div style={{ color:accent, fontWeight:"bold", fontSize:13 }}>{typeof v === 'number' ? v.toFixed(4) : v}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 1: NSDT */}
        {tab === 1 && (
          <div style={ss.row}>
            <div style={ss.col(2)}>
              <div style={ss.panel()}>
                <div style={ss.label}>NSDT VECTOR — Adjust sliders to set system state</div>
                {[
                  ["complexity",   "C", "#9b59b6", nsdt.c],
                  ["stability",    "S", "#2ecc71", nsdt.s],
                  ["tension",      "T", "#e74c3c", nsdt.t],
                  ["adaptability", "A", "#3498db", nsdt.a],
                  ["coherence",    "CO","#f1c40f", nsdt.co],
                ].map(([key, label, color, val]) => (
                  <div key={key} style={{ marginBottom:14 }}>
                    <div style={{ display:"flex", justifyContent:"space-between", marginBottom:4 }}>
                      <span style={{ color, fontWeight:"bold", fontSize:12 }}>{label} — {key.toUpperCase()}</span>
                      <span style={{ color, fontWeight:"bold" }}>{val}%</span>
                    </div>
                    <input type="range" min={0} max={100} value={val}
                           onChange={e => setN(key === "coherence" ? "co" : key[0] === "c" ? "c" : key === "stability" ? "s" : key === "tension" ? "t" : "a", parseInt(e.target.value))}
                           style={{ ...ss.slider, accentColor:color }} />
                    <div style={{ height:4, background:"#111", borderRadius:2, marginTop:4 }}>
                      <div style={{ height:4, width:`${val}%`, background:color, borderRadius:2 }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div style={ss.col(2)}>
              <div style={ss.panel(accent)}>
                <div style={ss.label}>STAGE MATCH</div>
                <div style={{ ...ss.value(accent), fontSize:22 }}>
                  {STAGE_META[sap.macro].emoji} {STAGE_META[sap.macro].star}
                </div>
                <div style={{ color:C.text }}>{STAGE_META[sap.macro].name} · {sap.confidence}% confidence</div>
                <div style={{ marginTop:8, fontSize:11, color:C.dim }}>
                  Address: {sap.fractal_addr}
                </div>
              </div>

              <div style={ss.panel()}>
                <div style={ss.label}>ALL STAGE MATCHES</div>
                {sap.all_distances.map(({ stage, dist }) => {
                  const meta = STAGE_META[stage];
                  const pct = Math.max(0, (1 - dist) * 100);
                  return (
                    <div key={stage} style={{ marginBottom:6 }}>
                      <div style={{ display:"flex", justifyContent:"space-between", fontSize:10, marginBottom:2 }}>
                        <span style={{ color: stage===sap.macro ? meta.accent : C.dim }}>{meta.emoji} Stage {stage} — {meta.name}</span>
                        <span style={{ color:C.dim }}>{dist.toFixed(3)}</span>
                      </div>
                      <div style={{ height:3, background:"#111", borderRadius:2 }}>
                        <div style={{ height:3, width:`${pct}%`, background:meta.accent, borderRadius:2 }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: TRAPSCORE */}
        {tab === 2 && (
          <div style={ss.row}>
            <div style={ss.col(1)}>
              <div style={ss.panel()}>
                <div style={ss.label}>TRAPSCORE = S × R × (1 − A)</div>
                <div style={{ textAlign:"center", padding:"20px 0" }}>
                  <div style={{ fontSize:60, fontWeight:"bold", color:
                    sap.trapscore > 0.75 ? "#e74c3c" : sap.trapscore > 0.5 ? "#e67e22" : sap.trapscore > 0.25 ? "#f39c12" : "#2ecc71"
                  }}>
                    {(sap.trapscore * 100).toFixed(0)}%
                  </div>
                  <div style={{ color:C.dim, marginTop:8 }}>
                    {sap.trapscore > 0.75 ? "⚠️ CRITICAL LOCK" : sap.trapscore > 0.5 ? "TRAPPED" : sap.trapscore > 0.25 ? "WATCH" : "✓ FREE"}
                  </div>
                  <div style={{ marginTop:12, fontSize:11, color:C.dim }}>
                    T({(nsdt.t/100).toFixed(2)}) × S({(nsdt.s/100).toFixed(2)}) × (1−A({(nsdt.a/100).toFixed(2)})) = {sap.trapscore.toFixed(4)}
                  </div>
                </div>
              </div>

              <div style={ss.panel()}>
                <div style={ss.label}>SAP STAGE EQUIVALENCY</div>
                {[["0–25%","Stages 0–4","Green Zone — Flow and growth possible"],
                  ["25–50%","Stage 5","Threshold Zone — Choose quickly"],
                  ["50–75%","Stage 7–8","Danger Zone — Rigidity forming"],
                  ["75–100%","Stage 8 LOCK","Critical — Deliberate un-learning required"],
                ].map(([range, stage, desc]) => (
                  <div key={range} style={{ padding:"6px 0", borderBottom:`1px solid ${C.border}` }}>
                    <div style={{ display:"flex", gap:12, fontSize:11 }}>
                      <span style={{ color:accent, width:60 }}>{range}</span>
                      <span style={{ color:C.text, width:90 }}>{stage}</span>
                      <span style={{ color:C.dim }}>{desc}</span>
                    </div>
                  </div>
                ))}
              </div>

              {sap.macro === 8 && (
                <div style={ss.panel(C.trap.CRITICAL)}>
                  <div style={{ color:C.trap.CRITICAL, fontWeight:"bold", marginBottom:8 }}>⚠️ STAGE 8 RELEASE PROTOCOL</div>
                  {["Practice gratitude — identify 5 genuine sources daily.",
                    "Master duality — hold opposites without collapsing into either.",
                    "Ma'at forgiveness — declare your transgression, release it, move forward.",
                    "Deep witnessing — observe the trap without judgment.",
                    "Deliberately un-learn one assumption you hold as absolute truth."
                  ].map((item, i) => (
                    <div key={i} style={{ fontSize:11, color:C.text, marginBottom:4 }}>• {item}</div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 3: MA'AT */}
        {tab === 3 && (
          <div>
            <div style={ss.row}>
              <div style={ss.col(1)}>
                <div style={ss.panel(C.badge[maat.badge])}>
                  <div style={{ textAlign:"center" }}>
                    <div style={{ fontSize:48, fontWeight:"bold", color:C.badge[maat.badge] }}>{maat.score}%</div>
                    <div style={{ color:C.badge[maat.badge], letterSpacing:3 }}>{maat.badge.toUpperCase()}</div>
                  </div>
                  {maat.violations.length > 0 && (
                    <div style={{ marginTop:12 }}>
                      <div style={ss.label}>VIOLATIONS ({maat.violations.length})</div>
                      {maat.violations.map(v => (
                        <div key={v} style={ss.alert_crit}>{v}</div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
              <div style={ss.col(2)}>
                <div style={ss.panel()}>
                  <div style={ss.label}>42 PRINCIPLES OF MA'AT</div>
                  <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:4, marginTop:8 }}>
                    {MAAT_TRIGGERS.map(p => (
                      <div key={p.name} style={{ padding:"4px 6px", borderRadius:3, fontSize:10,
                            background: maat.violations.includes(p.name) ? "#1a0505" : "#060b12",
                            border:`1px solid ${maat.violations.includes(p.name) ? "#e74c3c" : C.border}`,
                            color: maat.violations.includes(p.name) ? "#e74c3c" : C.dim }}>
                        {maat.violations.includes(p.name) ? "✗" : "✓"} {p.name}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            <div style={ss.panel()}>
              <div style={ss.label}>EPISTEMIC HUMILITY — YUNUS PROTOCOL</div>
              <div style={{ fontSize:12, color: yunus.score > 70 ? "#2ecc71" : "#e74c3c", fontWeight:"bold", marginBottom:8 }}>
                Score: {yunus.score}% · Arrogance Markers: {yunus.arroganceHits}
              </div>
              {yunus.flags.map((f, i) => (
                <div key={i} style={{ fontSize:11, color: f.startsWith("✓") ? "#2ecc71" : "#e74c3c", marginBottom:4 }}>{f}</div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 4: CONSENSUS */}
        {tab === 4 && (
          <div>
            <div style={ss.row}>
              <div style={ss.col(1)}>
                <div style={ss.panel(accent)}>
                  <div style={ss.label}>MYCELIAL CONSENSUS — 5 Independent Evaluators</div>
                  <div style={{ ...ss.value(accent), fontSize:22, marginBottom:4 }}>
                    {STAGE_META[consensus.consensusStage].emoji} Stage {consensus.consensusStage} — {STAGE_META[consensus.consensusStage].name}
                  </div>
                  <div style={{ display:"flex", gap:12, marginBottom:8 }}>
                    {[["AGREEMENT",`${consensus.agreement}%`],["UNCERTAINTY",`${(consensus.uncertainty*100).toFixed(0)}%`],
                      ["INTERVAL",`${consensus.interval[0]}–${consensus.interval[1]}`]].map(([l,v]) => (
                      <div key={l} style={{ textAlign:"center", flex:1 }}>
                        <div style={ss.label}>{l}</div>
                        <div style={{ color:accent, fontWeight:"bold" }}>{v}</div>
                      </div>
                    ))}
                  </div>
                  <div style={{ fontSize:11, color: consensus.uncertainty > 0.35 ? "#e67e22" : "#2ecc71" }}>
                    {consensus.integrity}
                  </div>
                </div>
              </div>
            </div>

            <div style={ss.row}>
              {consensus.votes.map(vote => (
                <div key={vote.name} style={{ ...ss.col(1), ...ss.panel(vote.color) }}>
                  <div style={{ color:vote.color, fontWeight:"bold", fontSize:12, marginBottom:4 }}>{vote.label}</div>
                  <div style={{ ...ss.value(vote.color), fontSize:20 }}>
                    {STAGE_META[vote.stageVote].emoji} Stage {vote.stageVote}
                  </div>
                  <div style={{ color:C.dim, fontSize:10, marginTop:4 }}>{vote.confidence.toFixed(1)}% confidence</div>
                  <div style={{ fontSize:10, color:C.text, marginTop:6 }}>
                    {vote.stageVote !== consensus.consensusStage ? `⚠️ Dissents from consensus (${consensus.consensusStage})` : "✓ Agrees with consensus"}
                  </div>
                </div>
              ))}
            </div>

            <div style={ss.panel()}>
              <div style={ss.label}>CONSENSUS RECOMMENDATION</div>
              <div style={{ fontSize:12, color:C.text }}>
                {STAGE_META[consensus.consensusStage].release}
                {consensus.uncertainty > 0.4 && (
                  <span style={{ color:"#e67e22" }}> High uncertainty — also examine Stages {consensus.interval[0]}–{consensus.interval[1]}. Seek additional data.</span>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 5: META-INTELLIGENCE */}
        {tab === 5 && (
          <div>
            <div style={ss.panel(accent)}>
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                <div>
                  <div style={ss.label}>CENTER OF GRAVITY — 10-Module Average</div>
                  <div style={{ ...ss.value(accent), fontSize:28 }}>Stage {meta.avg.toFixed(2)}</div>
                </div>
                <div style={{ textAlign:"right" }}>
                  <div style={ss.label}>LEADING EDGE</div>
                  <div style={{ color:accent, fontWeight:"bold" }}>{meta.leading}</div>
                  <div style={ss.label}>GROWING EDGE</div>
                  <div style={{ color:"#e67e22", fontWeight:"bold" }}>{meta.growing}</div>
                </div>
              </div>
            </div>

            <div style={{ display:"grid", gridTemplateColumns:"repeat(5,1fr)", gap:12 }}>
              {Object.entries(meta.scores).map(([mod, score]) => {
                const pct = (score / 9) * 100;
                const isLeading = mod === meta.leading;
                const isGrowing = mod === meta.growing;
                const modColor = isLeading ? accent : isGrowing ? "#e67e22" : C.dim;
                const emojis = { paradox:"⟳", myth:"⚔", emotion:"♥", temporal:"◷", geometry:"✦", liminality:"◈", linguistic:"✎", somatic:"◎", emergence:"✺", metacognition:"∞" };
                return (
                  <div key={mod} style={ss.panel(isLeading ? accent : isGrowing ? "#e67e22" : undefined)}>
                    <div style={{ color:modColor, fontSize:20, marginBottom:4 }}>{emojis[mod] || "○"}</div>
                    <div style={{ color:modColor, fontWeight:"bold", fontSize:11, marginBottom:6 }}>{mod.toUpperCase()}</div>
                    <div style={{ ...ss.value(modColor), fontSize:18 }}>{score.toFixed(1)}</div>
                    <div style={{ height:3, background:"#111", borderRadius:2, marginTop:6 }}>
                      <div style={{ height:3, width:`${pct}%`, background:modColor, borderRadius:2 }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* TAB 6: INFRASTRUCTURE */}
        {tab === 6 && (
          <div style={ss.row}>
            <div style={ss.col(1)}>
              <div style={ss.panel()}>
                <div style={ss.label}>SYSTEM</div>
                <select value={infraSystem} onChange={e => setInfraSystem(e.target.value)}
                        style={{ background:"#060b12", border:`1px solid ${C.border}`, color:C.text, padding:"4px 8px", borderRadius:4, width:"100%", fontFamily:"inherit" }}>
                  {["water","nuclear","vehicle","supply_chain","hospital"].map(s => (
                    <option key={s} value={s}>{s.replace("_"," ").toUpperCase()}</option>
                  ))}
                </select>

                {infraSystem === "water" && (
                  <div style={{ marginTop:12 }}>
                    {[["lead_ppb","Lead (ppb)",0,100],["ph_drop","pH Drop",0,2],
                      ["complaint_increase_pct","Complaints % ↑",0,500],["ci_reduction_pct","CI Reduction %",0,100],
                      ["funding_ratio","Funding Ratio",0,2]].map(([key,label,min,max]) => (
                      <div key={key} style={{ marginBottom:8 }}>
                        <div style={{ display:"flex", justifyContent:"space-between", fontSize:11, marginBottom:2 }}>
                          <span style={{ color:C.dim }}>{label}</span>
                          <span style={{ color:C.text }}>{infraData[key]}</span>
                        </div>
                        <input type="range" min={min} max={max} step={key==="ph_drop"||key==="funding_ratio"?0.1:1}
                               value={infraData[key]||0}
                               onChange={e => setInfraData(d => ({...d,[key]:parseFloat(e.target.value)}))}
                               style={ss.slider} />
                      </div>
                    ))}
                    <div style={{ marginBottom:8 }}>
                      <div style={ss.label}>DEMOGRAPHICS (type "minority" to flag)</div>
                      <input value={infraData.demographics_majority} onChange={e => setInfraData(d => ({...d,demographics_majority:e.target.value}))}
                             style={{ width:"100%", background:"#060b12", border:`1px solid ${C.border}`, color:C.text, padding:"4px 8px", borderRadius:4, fontFamily:"inherit", boxSizing:"border-box" }} />
                    </div>
                  </div>
                )}

                <button onClick={runInfra} style={{ ...ss.btn(accent), marginTop:8 }}>▶ RUN ANALYSIS</button>
              </div>
            </div>

            <div style={ss.col(2)}>
              {infraResult && (
                <div style={ss.panel()}>
                  <div style={ss.label}>INFRASTRUCTURE ANALYSIS — {infraResult.system.toUpperCase()}</div>
                  <div style={{ ...ss.value(infraResult.risk > 0.7 ? "#e74c3c" : infraResult.risk > 0.4 ? "#e67e22" : "#2ecc71"), fontSize:32, marginBottom:8 }}>
                    {(infraResult.risk * 100).toFixed(0)}% RISK
                  </div>
                  {infraResult.alerts.map((a, i) => (
                    <div key={i} style={a.startsWith("🚨") ? ss.alert_crit : ss.alert_warn}>{a}</div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 7: HISTORY */}
        {tab === 7 && (
          <div>
            {history.length === 0 ? (
              <div style={{ ...ss.panel(), textAlign:"center", color:C.dim, padding:40 }}>
                No analysis history yet. Run an analysis to begin building trajectory data.
              </div>
            ) : (
              <>
                <div style={ss.panel(yunusTraj.triggered ? "#e74c3c" : undefined)}>
                  <div style={ss.label}>TRAJECTORY INTELLIGENCE</div>
                  <div style={ss.row}>
                    {[
                      ["Readings", history.length],
                      ["Risk Momentum", (() => {
                        const stages = history.slice(-5).map(h => h.macro);
                        const deltas = stages.slice(1).map((s,i) => s - stages[i]);
                        return (deltas.reduce((a,b)=>a+b,0)/Math.max(deltas.length,1)).toFixed(2);
                      })()],
                      ["Trap Events", history.filter(h => ["CRITICAL","HIGH"].includes(h.trap_risk)).length],
                      ["Avg Ma'at", `${Math.round(history.reduce((s,h) => s+h.maat_score,0)/history.length)}%`],
                    ].map(([l,v]) => (
                      <div key={l} style={{ textAlign:"center", flex:1 }}>
                        <div style={ss.label}>{l}</div>
                        <div style={{ color:accent, fontWeight:"bold", fontSize:16 }}>{v}</div>
                      </div>
                    ))}
                  </div>
                  {yunusTraj.triggered && (
                    <div style={{ ...ss.alert_crit, marginTop:8 }}>{yunusTraj.message}</div>
                  )}
                </div>

                {[...history].reverse().map((snap, i) => {
                  const meta = STAGE_META[snap.macro];
                  return (
                    <div key={i} style={ss.panel()}>
                      <div style={{ display:"flex", gap:12, alignItems:"center" }}>
                        <div style={{ color:meta.accent, fontSize:18 }}>{meta.emoji}</div>
                        <div style={{ flex:1 }}>
                          <div style={{ color:meta.accent, fontWeight:"bold", fontSize:12 }}>
                            Stage {snap.macro}.{snap.micro} — {meta.name}
                          </div>
                          <div style={{ color:C.dim, fontSize:10, marginTop:2 }}>
                            {new Date(snap.ts).toLocaleTimeString()} · {snap.text_preview}
                          </div>
                        </div>
                        <div style={{ display:"flex", gap:8 }}>
                          {[["TRAP",snap.trap_risk,C.trap[snap.trap_risk]],
                            ["Ma'at",`${snap.maat_score}%`,"#2ecc71"],
                            ["TS",`${(snap.trapscore*100).toFixed(0)}%`,snap.trapscore>0.5?"#e74c3c":"#2ecc71"]
                          ].map(([l,v,c]) => (
                            <div key={l} style={{ textAlign:"center" }}>
                              <div style={{ fontSize:9, color:C.dim }}>{l}</div>
                              <div style={{ fontSize:11, color:c, fontWeight:"bold" }}>{v}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </>
            )}
          </div>
        )}
      </div>

      {/* FOOTER */}
      <div style={{ background:C.header, borderTop:`1px solid ${C.border}`, padding:"8px 20px", display:"flex", justifyContent:"space-between", fontSize:10, color:C.dim }}>
        <span>LUMINARK OVERWATCH PRIME v4.0 | Richard L. Stanfield | METATRON Align With Purpose</span>
        <span>ALWAYS WATCHING · NEVER INTERRUPTING · READY WHEN YOU ARE</span>
        <span>81 Addressable Macro-Micro Positions · 9^4 = 6,561 Pico-Level Resolution</span>
      </div>
    </div>
  );
}
