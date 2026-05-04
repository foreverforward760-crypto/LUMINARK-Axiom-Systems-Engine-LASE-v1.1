import { useState, useEffect, useCallback } from "react";

// ═══════════════════════════════════════════════════════
//  SAP CORE DATA
// ═══════════════════════════════════════════════════════
const STAGES = {
  0: { name:"Plenara",       short:"PLN", icon:"○", color:"#0d0d1a", accent:"#4a4aaa", desc:"Pure potential. Complete dissolution. Still point between cycles." },
  1: { name:"Emergence",     short:"EMG", icon:"◑", color:"#0f1e38", accent:"#5a9fd8", desc:"The initial spark materializes. Birth of form." },
  2: { name:"Polarity",      short:"POL", icon:"◐", color:"#1a0f38", accent:"#e06080", desc:"Divergent forces create definition. Binary choices." },
  3: { name:"Expression",    short:"EXP", icon:"△", color:"#1e1038", accent:"#c077ff", desc:"Creative growth. First self-reflection + 3D complexity." },
  4: { name:"Foundation",    short:"FDN", icon:"□", color:"#0f2010", accent:"#60b237", desc:"Consolidation. Reliable structures form. Stability integrates." },
  5: { name:"Threshold",     short:"THR", icon:"◇", color:"#382010", accent:"#ff9a3c", desc:"Critical pivot. Bifurcation point. Rise or fall decided here." },
  6: { name:"Harmony",       short:"HRM", icon:"✦", color:"#083040", accent:"#7ad4c8", desc:"Integration and flow. Elements unify. Peak efficiency." },
  7: { name:"Distillation",  short:"DST", icon:"◁", color:"#301040", accent:"#d880d8", desc:"Refinement. Elimination of inefficiencies. Growing tension." },
  8: { name:"Atlas",         short:"ATL", icon:"⚠", color:"#301010", accent:"#ff5050", desc:"False hell. Attractor lock. TRAP ZONE. Gratitude releases polarity toward Stage 9." },
  9: { name:"Transformation",short:"TRX", icon:"◎", color:"#0d1820", accent:"#f0c040", desc:"Shattering and renewal. Cycle closes. Transparent return." },
};

const NSDT_CENTROIDS = {
  0:[0.00,0.00,0.00,0.10,0.00], 1:[0.15,0.15,0.20,0.30,0.15],
  2:[0.25,0.25,0.45,0.40,0.20], 3:[0.35,0.35,0.40,0.45,0.35],
  4:[0.45,0.75,0.30,0.50,0.55], 5:[0.55,0.40,0.70,0.55,0.45],
  6:[0.65,0.70,0.35,0.65,0.70], 7:[0.75,0.60,0.55,0.60,0.65],
  8:[0.85,0.50,0.75,0.35,0.80], 9:[0.95,0.30,0.90,0.80,0.90],
};

const TRAP_RISK = (m,mi) => {
  if(m===8&&mi>=6) return "CRITICAL";
  if(m===8) return "HIGH";
  if(mi===8) return "HIGH";
  if(m===7&&mi>=7) return "ELEVATED";
  if(m===5) return "WATCH";
  if(mi===5) return "WATCH";
  return "LOW";
};

const RISK_COLOR = { CRITICAL:"#ff2020", HIGH:"#ff6020", ELEVATED:"#ff9a3c", WATCH:"#f0c040", LOW:"#60b237" };

const MAAT_42 = [
  ["Truth","I have not spoken falsely"],
  ["Justice","I have not committed injustice"],
  ["Balance","I have not disturbed the balance"],
  ["Reciprocity","I have not acted without reciprocity"],
  ["Order","I have not disturbed natural order"],
  ["Harmony","I have not disrupted harmony"],
  ["Honor","I have not spoken dishonorably"],
  ["Compassion","I have not failed compassion"],
  ["NonViolence","I have not committed violence"],
  ["Gratitude","I have not been ungrateful"],
  ["Humility","I have not been arrogant"],
  ["Curiosity","I have not closed my mind"],
  ["Patience","I have not been impatient"],
  ["Silence","I have not spoken when silence required"],
  ["Transparency","I have not been opaque"],
  ["Ownership","I have not failed responsibility"],
  ["Service","I have not refused to serve"],
  ["Wisdom","I have not acted without wisdom"],
  ["Courage","I have not acted from cowardice"],
  ["Integrity","I have not betrayed integrity"],
  ["Perspective","I have not lost perspective"],
  ["Resilience","I have not abandoned resilience"],
  ["Creativity","I have not suppressed creativity"],
  ["Connection","I have not severed connection"],
  ["Growth","I have not refused growth"],
  ["Flow","I have not blocked the flow"],
  ["Release","I have not failed to release"],
  ["Acceptance","I have not refused what is"],
  ["Boundaries","I have not violated boundaries"],
  ["Authenticity","I have not been inauthentic"],
  ["Presence","I have not abandoned the present"],
  ["Discernment","I have not failed to discern"],
  ["Protection","I have not failed to protect"],
  ["Equanimity","I have not abandoned equanimity"],
  ["Sovereignty","I have not surrendered sovereignty"],
  ["Purpose","I have not acted without purpose"],
  ["Inclusion","I have not excluded unjustly"],
  ["Evolution","I have not refused evolution"],
  ["Sacred","I have not profaned the sacred"],
  ["Witness","I have not failed true witness"],
  ["Stewardship","I have not failed stewardship"],
  ["Completion","I have not abandoned what I began"],
];

const META_MODULES = [
  { id:"paradox",    name:"Paradox",       icon:"⟳", desc:"Both/and capacity. Contradiction holding." },
  { id:"myth",       name:"Myth",          icon:"⚔", desc:"Hero's Journey. Archetypal pattern recognition." },
  { id:"emotion",    name:"Emotion",       icon:"♥", desc:"Emotional signature & granularity mapping." },
  { id:"temporal",   name:"Temporal",      icon:"◷", desc:"Time horizon & simultaneity awareness." },
  { id:"geometry",   name:"Geometry",      icon:"✦", desc:"Sacred pattern & structural recognition." },
  { id:"liminality", name:"Liminality",    icon:"◈", desc:"Threshold & in-between state detection." },
  { id:"linguistic", name:"Linguistic",    icon:"✎", desc:"Spiral Dynamics vMeme language mapping." },
  { id:"somatic",    name:"Somatic",       icon:"◎", desc:"Nervous system state & body intelligence." },
  { id:"emergence",  name:"Emergence",     icon:"✺", desc:"Phase transition & tipping point detection." },
  { id:"meta",       name:"MetaCognition", icon:"∞", desc:"Recursive self-awareness depth." },
];

// ═══════════════════════════════════════════════════════
//  COMPUTATION ENGINE
// ═══════════════════════════════════════════════════════
function euclidean(a, b) {
  return Math.sqrt(a.reduce((sum,v,i) => sum + (v-b[i])**2, 0));
}

function assessNSDT(vec) {
  const entries = Object.entries(NSDT_CENTROIDS);
  const dists = entries.map(([s,c]) => [parseInt(s), euclidean(vec, c)]);
  dists.sort((a,b)=>a[1]-b[1]);
  const [macro, d0] = dists[0], [next, d1] = dists[1];
  const conf = 1 - d0/(d0+d1+1e-9);
  const blend = d0/(d0+d1+1e-9);
  const micro = Math.max(0, Math.min(9, Math.round(Math.abs((next-macro)*blend)*10)));
  const nano = Math.round(vec[2]*9);
  const pico = Math.round(vec[4]*9);
  return { macro, micro, nano, pico, confidence: conf, trap: TRAP_RISK(macro, micro),
           addr: `${macro}.${micro}.${nano}.${pico}` };
}

function calcTrapscore(S, R, A) { return Math.max(0, Math.min(1, S*R*(1-A))); }

function analyzeText(text) {
  const words = text.toLowerCase().split(/\s+/);
  const wc = Math.max(words.length, 1);
  const avgLen = words.reduce((s,w)=>s+w.length,0)/wc;
  const complexity = Math.min(1, avgLen/12);
  const stableW = new Set(["therefore","established","consistent","reliable","clear","structured","grounded"]);
  const chaosW = new Set(["confused","lost","overwhelmed","scattered","fragmented","crisis","spiraling"]);
  const tensionW = new Set(["but","however","conflict","tension","struggle","versus","problem","danger","fear"]);
  const adaptW = new Set(["maybe","perhaps","could","explore","learn","adapt","change","evolve","consider"]);
  const cohW = new Set(["therefore","thus","hence","because","since","consequently"]);
  let s=0,c=0,t=0,a=0,co=0;
  words.forEach(w => {
    if(stableW.has(w)) s++;
    if(chaosW.has(w)) c++;
    if(tensionW.has(w)) t++;
    if(adaptW.has(w)) a++;
    if(cohW.has(w)) co++;
  });
  return [
    Math.min(1, complexity),
    Math.max(0, Math.min(1, 0.5 + (s-c)/wc*5)),
    Math.min(1, t/wc*10),
    Math.min(1, a/wc*8),
    Math.min(1, 0.3 + co/5),
  ];
}

function analyzeMaat(text) {
  const violations = [];
  const tl = text.toLowerCase();
  const checks = [
    ["Truth",["lie","deceive","false","fabricate"]],
    ["Balance",["extreme","one-sided","biased"]],
    ["Humility",["100%","undeniable","certain i am right","perfect","impossible to fail","arrogant"]],
    ["NonViolence",["harm","destroy","attack"]],
    ["Justice",["unfair","unjust","discriminate"]],
    ["Integrity",["betray","corrupt","sell out"]],
  ];
  checks.forEach(([p,kws]) => { if(kws.some(k=>tl.includes(k))) violations.push(p); });
  const score = Math.max(0, 1 - violations.length*0.15);
  return { score: Math.round(score*100)/100, violations, badge: score>=0.85?"pass":score>=0.6?"caution":"fail" };
}

function analyzeMetaModules(text) {
  const tl = text.toLowerCase();
  return {
    paradox: { stage: Math.min(9, 1 + ["both","and yet","simultaneously","paradox"].filter(k=>tl.includes(k)).length*2), insight: "Paradox capacity measured" },
    myth: { stage: tl.includes("threshold")||tl.includes("crossing")?5.5:tl.includes("transform")?8:4, insight: "Hero's Journey mapped" },
    emotion: { stage: Math.min(9, ["joy","grief","anger","fear","hope","love","awe"].filter(k=>tl.includes(k)).length*1.3), insight: "Emotional granularity assessed" },
    temporal: { stage: tl.includes("universe")||tl.includes("cosmos")?9:tl.includes("generation")?7:tl.includes("decade")?5.5:4, insight: "Time horizon mapped" },
    geometry: { stage: tl.includes("fractal")?9:tl.includes("spiral")?7:tl.includes("pattern")?6:4, insight: "Sacred geometry detected" },
    liminality: { stage: Math.min(9, 4.5+["between","neither","threshold","crossing","in-between"].filter(k=>tl.includes(k)).length*0.8), insight: "Liminal state measured" },
    linguistic: { stage: tl.includes("integral")||tl.includes("systems")?7.5:tl.includes("community")||tl.includes("inclusive")?6:5, insight: "Spiral Dynamics mapped" },
    somatic: { stage: tl.includes("safe")||tl.includes("calm")||tl.includes("grounded")?8:tl.includes("freeze")||tl.includes("numb")?1:3, insight: "Nervous system assessed" },
    emergence: { stage: Math.min(9, 5+["breakthrough","tipping","emerged","suddenly"].filter(k=>tl.includes(k)).length*1.5), insight: "Phase transition probability" },
    meta: { stage: Math.min(9, 4+["i notice","i observe","perspective","watching myself"].filter(k=>tl.includes(k)).length*1.5), insight: "Meta-cognitive depth measured" },
  };
}

// ═══════════════════════════════════════════════════════
//  MAIN COMPONENT
// ═══════════════════════════════════════════════════════
const TABS = ["Navigator","NSDT","TrapScore","Ma'at","Meta-Intel","Infrastructure","History"];
const TAB_ICONS = ["🔭","🧬","⚠","⚖","🧠","🏗","📜"];

export default function LuminarkV3() {
  const [tab, setTab] = useState(0);
  const [level, setLevel] = useState(0);
  const [macro, setMacro] = useState(4);
  const [micro, setMicro] = useState(0);
  const [nano, setNano] = useState(0);
  const [pico, setPico] = useState(0);
  const [nsdt, setNsdt] = useState([0.45,0.75,0.30,0.50,0.55]);
  const [sapPos, setSapPos] = useState({macro:4,micro:0,nano:0,pico:0,confidence:0.8,trap:"LOW",addr:"4.0.0.0"});
  const [tsScore, setTsScore] = useState(0);
  const [textInput, setTextInput] = useState("");
  const [maatResult, setMaatResult] = useState({score:1,violations:[],badge:"pass"});
  const [metaResults, setMetaResults] = useState({});
  const [history, setHistory] = useState([]);
  const [visitedCells, setVisitedCells] = useState(new Set());
  const [infraSystem, setInfraSystem] = useState("water");
  const [infraData, setInfraData] = useState({lead_ppb:0,ph_drop:0,complaint_increase_pct:0,demographics_majority:"",funding_ratio:1});
  const [infraResult, setInfraResult] = useState(null);
  const [culturalCtx, setCulturalCtx] = useState({code_switching:false,historical_trauma:false,systemic_oppression:false});

  const stage = STAGES[macro];

  // Recompute trap risk whenever position changes
  useEffect(() => {
    const ts = calcTrapscore(nsdt[1], 1-nsdt[3], nsdt[3]);
    setTsScore(ts);
  }, [nsdt]);

  const runFullAnalysis = useCallback(() => {
    if (!textInput.trim()) return;
    const vec = analyzeText(textInput);
    setNsdt(vec);
    const pos = assessNSDT(vec);
    setSapPos(pos);
    setMacro(pos.macro);
    setMicro(pos.micro);
    setNano(pos.nano);
    setPico(pos.pico);
    const maat = analyzeMaat(textInput);
    setMaatResult(maat);
    const meta = analyzeMetaModules(textInput);
    setMetaResults(meta);
    const cellKey = level===0?pos.macro:level===1?`${pos.macro}.${pos.micro}`:level===2?`${pos.macro}.${pos.micro}.${pos.nano}`:`${pos.macro}.${pos.micro}.${pos.nano}.${pos.pico}`;
    setVisitedCells(prev => new Set([...prev, cellKey]));
    const entry = {
      ts: new Date().toLocaleTimeString(),
      text: textInput.slice(0,60)+"…",
      macro: pos.macro, micro: pos.micro,
      stageName: STAGES[pos.macro].name,
      trap: pos.trap,
      maat: maat.score,
      trapscore: calcTrapscore(vec[1],1-vec[3],vec[3]),
      metaAvg: Object.values(meta).reduce((s,m)=>s+m.stage,0)/10,
    };
    setHistory(prev=>[entry,...prev].slice(0,50));
    setTab(0);
  }, [textInput, level]);

  const handleNsdtChange = (idx, val) => {
    const newVec = [...nsdt]; newVec[idx]=val;
    setNsdt(newVec);
    const pos = assessNSDT(newVec);
    setSapPos(pos); setMacro(pos.macro); setMicro(pos.micro); setNano(pos.nano); setPico(pos.pico);
  };

  const runInfra = () => {
    // Simplified infra scoring
    let risk=0, alerts=[], pattern="none";
    if(infraSystem==="water") {
      if(infraData.lead_ppb>5){risk+=0.35;alerts.push(`Lead ${infraData.lead_ppb}ppb exceeds threshold`);}
      if(infraData.ph_drop>0.4){risk+=0.25;alerts.push("pH drop matches Flint pattern");}
      if(infraData.complaint_increase_pct>200){risk+=0.20;alerts.push("Community complaints surging");}
      const demo=infraData.demographics_majority;
      if(["Black","Latino","Indigenous"].includes(demo)&&infraData.funding_ratio<0.8){risk=Math.min(1,risk+0.15);alerts.push("Structural inequity: underfunded minority system");}
      if(alerts.length>=3){pattern="FLINT";alerts.push("🚨 FLINT CRISIS PATTERN DETECTED");}
    }
    setInfraResult({system:infraSystem,risk:Math.min(1,risk),sap:Math.max(1,5-risk*4),alerts,pattern});
  };

  const NSDT_LABELS = ["Complexity","Stability","Tension","Adaptability","Coherence"];
  const NSDT_COLORS = ["#c077ff","#60b237","#ff9a3c","#7ad4c8","#5a9fd8"];

  // ─── RENDER GRID ─────────────────────────────────────
  const renderGrid = () => {
    const COLS = 10;
    const cells = [];
    for (let r=0; r<COLS; r++) {
      for (let c=0; c<COLS; c++) {
        const stage_idx = r;
        const micro_idx = c;
        const isActive = macro===stage_idx && micro===micro_idx;
        const isVisited = visitedCells.has(level===0?stage_idx:`${stage_idx}.${micro_idx}`);
        const risk = TRAP_RISK(stage_idx, micro_idx);
        const st = STAGES[stage_idx];
        const isTrap = stage_idx===8||(micro_idx===8&&stage_idx>3);
        const isThresh = stage_idx===5;
        return (
          <div
            key={`${r}-${c}`}
            onClick={() => {setMacro(stage_idx);setMicro(micro_idx);}}
            style={{
              background: isActive ? st.accent : isTrap ? "rgba(255,50,50,0.15)" : isThresh ? "rgba(255,154,60,0.12)" : isVisited ? "rgba(255,255,255,0.05)" : "rgba(255,255,255,0.02)",
              border: isActive ? `2px solid ${st.accent}` : isTrap ? "1px solid rgba(255,80,80,0.4)" : "1px solid rgba(255,255,255,0.07)",
              borderRadius: "4px",
              cursor: "pointer",
              padding: "4px",
              display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
              minHeight: "46px",
              transition: "all 0.15s",
              position: "relative",
            }}
          >
            <div style={{fontSize:"10px",color: isActive?"#000":st.accent,fontWeight:"bold"}}>{stage_idx}.{micro_idx}</div>
            <div style={{fontSize:"8px",color:"rgba(255,255,255,0.4)",marginTop:"2px"}}>{st.short}</div>
            {risk!=="LOW" && <div style={{position:"absolute",top:2,right:2,width:5,height:5,borderRadius:"50%",background:RISK_COLOR[risk]}}/>}
          </div>
        );
      }
    }
    // rebuild with proper row structure
    const rows = [];
    for(let r=0;r<COLS;r++){
      const rowCells=[];
      for(let c=0;c<COLS;c++){
        const stage_idx=r; const micro_idx=c;
        const isActive=macro===stage_idx&&micro===micro_idx;
        const isVisited=visitedCells.has(`${stage_idx}.${micro_idx}`);
        const risk=TRAP_RISK(stage_idx,micro_idx);
        const st=STAGES[stage_idx];
        const isTrap=stage_idx===8||(micro_idx===8&&stage_idx>3);
        const isThresh=stage_idx===5;
        rowCells.push(
          <div key={c} onClick={()=>{setMacro(stage_idx);setMicro(micro_idx);}}
            style={{flex:1,background:isActive?st.accent:isTrap?"rgba(255,50,50,0.15)":isThresh?"rgba(255,154,60,0.1)":isVisited?"rgba(255,255,255,0.05)":"rgba(255,255,255,0.02)",border:isActive?`2px solid ${st.accent}`:isTrap?"1px solid rgba(255,80,80,0.35)":"1px solid rgba(255,255,255,0.07)",borderRadius:"4px",cursor:"pointer",padding:"3px 2px",display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",minHeight:"44px",transition:"all 0.15s",position:"relative"}}>
            <div style={{fontSize:"9px",color:isActive?"#000":st.accent,fontWeight:"bold"}}>{stage_idx}.{micro_idx}</div>
            <div style={{fontSize:"7px",color:"rgba(255,255,255,0.35)"}}>{st.short}</div>
            {risk!=="LOW"&&<div style={{position:"absolute",top:1,right:2,width:4,height:4,borderRadius:"50%",background:RISK_COLOR[risk]}}/>}
          </div>
        );
      }
      rows.push(<div key={r} style={{display:"flex",gap:"3px"}}>{rowCells}</div>);
    }
    return rows;
  };

  // ─── TAB: NAVIGATOR ─────────────────────────────────
  const NavTab = () => (
    <div style={{display:"flex",gap:"16px",flexWrap:"wrap"}}>
      {/* Text analysis input */}
      <div style={{flex:"1 1 340px",background:"rgba(255,255,255,0.03)",borderRadius:"12px",padding:"16px",border:"1px solid rgba(255,255,255,0.08)"}}>
        <div style={{fontSize:"11px",color:"rgba(255,255,255,0.5)",marginBottom:"8px",letterSpacing:"0.1em"}}>ANALYZE ANY TEXT</div>
        <textarea value={textInput} onChange={e=>setTextInput(e.target.value)}
          placeholder="Paste any text — journal entry, conversation, system description, AI output... LUMINARK will assess its SAP stage, Ma'at alignment, and all 10 meta-intelligence dimensions."
          style={{width:"100%",height:"100px",background:"rgba(0,0,0,0.4)",border:"1px solid rgba(255,255,255,0.1)",borderRadius:"8px",color:"#fff",padding:"10px",fontSize:"13px",resize:"vertical",fontFamily:"inherit",boxSizing:"border-box"}}/>
        <div style={{marginTop:"8px",display:"flex",gap:"8px",flexWrap:"wrap"}}>
          {["code_switching","historical_trauma","systemic_oppression"].map(k=>(
            <label key={k} style={{display:"flex",alignItems:"center",gap:"5px",fontSize:"11px",color:"rgba(255,255,255,0.5)",cursor:"pointer"}}>
              <input type="checkbox" checked={culturalCtx[k]} onChange={e=>setCulturalCtx(p=>({...p,[k]:e.target.checked}))} style={{accentColor:"#7ad4c8"}}/>
              {k.replace(/_/g," ")}
            </label>
          ))}
        </div>
        <button onClick={runFullAnalysis}
          style={{marginTop:"10px",background:`linear-gradient(135deg, ${stage.accent}88, ${stage.accent})`,border:"none",borderRadius:"8px",color:"#fff",padding:"10px 20px",cursor:"pointer",fontWeight:"bold",fontSize:"13px",width:"100%"}}>
          ⚡ RUN FULL LUMINARK ANALYSIS
        </button>
      </div>

      {/* Current position panel */}
      <div style={{flex:"1 1 260px",background:`linear-gradient(135deg,${stage.color},rgba(0,0,0,0.6))`,borderRadius:"12px",padding:"16px",border:`1px solid ${stage.accent}44`}}>
        <div style={{fontSize:"42px",textAlign:"center"}}>{stage.icon}</div>
        <div style={{textAlign:"center",fontSize:"22px",fontWeight:"bold",color:stage.accent}}>{stage.name}</div>
        <div style={{textAlign:"center",fontSize:"13px",color:"rgba(255,255,255,0.5)",marginTop:"4px"}}>Stage {macro}.{micro}</div>
        <div style={{textAlign:"center",fontSize:"11px",color:"rgba(255,255,255,0.35)",marginTop:"4px"}}>Fractal: {sapPos.addr}</div>
        <div style={{marginTop:"12px",fontSize:"12px",color:"rgba(255,255,255,0.65)",lineHeight:"1.5",fontStyle:"italic"}}>{stage.desc}</div>
        <div style={{marginTop:"12px",padding:"8px",borderRadius:"8px",background:"rgba(0,0,0,0.3)",display:"flex",justifyContent:"space-between",alignItems:"center"}}>
          <span style={{fontSize:"11px",color:"rgba(255,255,255,0.5)"}}>TRAP RISK</span>
          <span style={{fontWeight:"bold",color:RISK_COLOR[sapPos.trap||"LOW"],fontSize:"13px"}}>{sapPos.trap||"LOW"}</span>
        </div>
        <div style={{marginTop:"6px",padding:"8px",borderRadius:"8px",background:"rgba(0,0,0,0.3)",display:"flex",justifyContent:"space-between",alignItems:"center"}}>
          <span style={{fontSize:"11px",color:"rgba(255,255,255,0.5)"}}>CONFIDENCE</span>
          <span style={{fontWeight:"bold",color:"#7ad4c8",fontSize:"13px"}}>{Math.round((sapPos.confidence||0.5)*100)}%</span>
        </div>
      </div>

      {/* Grid */}
      <div style={{flex:"2 1 500px",background:"rgba(255,255,255,0.02)",borderRadius:"12px",padding:"14px",border:"1px solid rgba(255,255,255,0.07)"}}>
        <div style={{fontSize:"11px",color:"rgba(255,255,255,0.4)",marginBottom:"10px",letterSpacing:"0.08em"}}>81-STAGE FRACTAL GRID — CLICK TO NAVIGATE</div>
        <div style={{display:"flex",flexDirection:"column",gap:"3px"}}>{renderGrid()}</div>
        <div style={{marginTop:"10px",display:"flex",gap:"12px",flexWrap:"wrap"}}>
          {[["TRAP",RISK_COLOR.HIGH],["THRESHOLD",RISK_COLOR.WATCH],["ACTIVE",stage.accent],["VISITED","rgba(255,255,255,0.2)"]].map(([l,c])=>(
            <div key={l} style={{display:"flex",alignItems:"center",gap:"5px",fontSize:"10px",color:"rgba(255,255,255,0.4)"}}>
              <div style={{width:10,height:10,borderRadius:"2px",background:c}}/>
              {l}
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // ─── TAB: NSDT ────────────────────────────────────────
  const NSDTTab = () => (
    <div style={{display:"flex",gap:"16px",flexWrap:"wrap"}}>
      <div style={{flex:"1 1 320px"}}>
        <div style={{background:"rgba(255,255,255,0.03)",borderRadius:"12px",padding:"16px",border:"1px solid rgba(255,255,255,0.08)"}}>
          <div style={{fontSize:"11px",color:"rgba(255,255,255,0.5)",marginBottom:"14px",letterSpacing:"0.1em"}}>5-VECTOR DIAGNOSTIC</div>
          {NSDT_LABELS.map((label,i)=>(
            <div key={i} style={{marginBottom:"16px"}}>
              <div style={{display:"flex",justifyContent:"space-between",marginBottom:"6px"}}>
                <span style={{fontSize:"12px",color:NSDT_COLORS[i],fontWeight:"bold"}}>{label}</span>
                <span style={{fontSize:"13px",color:"#fff",fontWeight:"bold"}}>{Math.round(nsdt[i]*100)}%</span>
              </div>
              <input type="range" min="0" max="100" value={Math.round(nsdt[i]*100)}
                onChange={e=>handleNsdtChange(i,parseInt(e.target.value)/100)}
                style={{width:"100%",accentColor:NSDT_COLORS[i]}}/>
              <div style={{marginTop:"4px",height:"6px",borderRadius:"3px",background:"rgba(0,0,0,0.3)"}}>
                <div style={{height:"100%",borderRadius:"3px",background:NSDT_COLORS[i],width:`${nsdt[i]*100}%`,transition:"width 0.3s"}}/>
              </div>
            </div>
          ))}
        </div>
      </div>
      <div style={{flex:"1 1 260px",display:"flex",flexDirection:"column",gap:"12px"}}>
        {/* Stage Match */}
        <div style={{background:`linear-gradient(135deg,${stage.color},rgba(0,0,0,0.6))`,borderRadius:"12px",padding:"16px",border:`1px solid ${stage.accent}44`}}>
          <div style={{fontSize:"11px",color:"rgba(255,255,255,0.5)",letterSpacing:"0.1em",marginBottom:"8px"}}>CLOSEST STAGE MATCH</div>
          <div style={{fontSize:"32px",textAlign:"center"}}>{stage.icon}</div>
          <div style={{textAlign:"center",fontSize:"20px",fontWeight:"bold",color:stage.accent}}>{stage.name}</div>
          <div style={{textAlign:"center",fontSize:"12px",color:"rgba(255,255,255,0.4)",marginTop:"4px"}}>Stage {macro}.{micro} · {Math.round((sapPos.confidence||0.5)*100)}% confidence</div>
        </div>
        {/* Top 3 stage distances */}
        <div style={{background:"rgba(255,255,255,0.03)",borderRadius:"12px",padding:"14px",border:"1px solid rgba(255,255,255,0.08)"}}>
          <div style={{fontSize:"11px",color:"rgba(255,255,255,0.5)",letterSpacing:"0.1em",marginBottom:"10px"}}>STAGE DISTANCES</div>
          {Object.entries(NSDT_CENTROIDS).map(([s,c])=>{
            const d = Math.round(Math.sqrt(nsdt.reduce((sum,v,i)=>sum+(v-c[i])**2,0))*1000)/1000;
            const st = STAGES[parseInt(s)];
            return (
              <div key={s} style={{display:"flex",alignItems:"center",gap:"8px",marginBottom:"6px"}}>
                <div style={{width:"20px",fontSize:"10px",color:st.accent,fontWeight:"bold"}}>{s}</div>
                <div style={{flex:1,height:"4px",borderRadius:"2px",background:"rgba(0,0,0,0.4)"}}>
                  <div style={{height:"100%",borderRadius:"2px",background:st.accent,width:`${Math.max(0,100-d*200)}%`}}/>
                </div>
                <div style={{fontSize:"10px",color:"rgba(255,255,255,0.4)",width:"40px",textAlign:"right"}}>{d.toFixed(3)}</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );

  // ─── TAB: TRAPSCORE ────────────────────────────────────
  const TrapTab = () => {
    const pct = tsScore * 100;
    const color = pct<25?"#60b237":pct<50?"#f0c040":pct<75?"#ff9a3c":"#ff5050";
    const label = pct<25?"FREE":pct<50?"WATCH":pct<75?"TRAPPED":"CRITICAL LOCK";
    return (
      <div style={{display:"flex",gap:"16px",flexWrap:"wrap"}}>
        <div style={{flex:"1 1 280px"}}>
          <div style={{background:"rgba(255,255,255,0.03)",borderRadius:"12px",padding:"24px",border:"1px solid rgba(255,255,255,0.08)",textAlign:"center"}}>
            <div style={{fontSize:"12px",color:"rgba(255,255,255,0.5)",letterSpacing:"0.12em",marginBottom:"16px"}}>TRAPSCORE MONITOR</div>
            <div style={{fontSize:"72px",fontWeight:"900",color:color}}>{Math.round(pct)}</div>
            <div style={{fontSize:"14px",color:color,fontWeight:"bold",letterSpacing:"0.08em"}}>{label}</div>
            <div style={{margin:"16px 0",height:"20px",borderRadius:"10px",background:"rgba(0,0,0,0.5)",overflow:"hidden"}}>
              <div style={{height:"100%",borderRadius:"10px",background:`linear-gradient(90deg,#60b237,#f0c040,#ff9a3c,#ff5050)`,width:`${pct}%`,transition:"width 0.5s"}}/>
            </div>
            <div style={{fontSize:"11px",color:"rgba(255,255,255,0.4)",fontFamily:"monospace",background:"rgba(0,0,0,0.3)",borderRadius:"6px",padding:"8px",marginTop:"8px"}}>
              S={Math.round(nsdt[1]*100)}% × R={Math.round((1-nsdt[3])*100)}% × (1−A={Math.round(nsdt[3]*100)}%) = <span style={{color,fontWeight:"bold"}}>{tsScore.toFixed(4)}</span>
            </div>
          </div>
        </div>
        <div style={{flex:"1 1 300px",display:"flex",flexDirection:"column",gap:"12px"}}>
          <div style={{background:"rgba(255,255,255,0.03)",borderRadius:"12px",padding:"16px",border:"1px solid rgba(255,255,255,0.08)"}}>
            <div style={{fontSize:"11px",color:"rgba(255,255,255,0.5)",letterSpacing:"0.1em",marginBottom:"12px"}}>SAP EQUIVALENCY</div>
            {[[0,0.25,"Stages 0-4","Free flow, healthy movement"],
              [0.25,0.5,"Stage 5","Threshold tension, watch carefully"],
              [0.5,0.75,"Stage 7-8","Distillation/Atlas trap zone"],
              [0.75,1.0,"Stage 8 LOCK","Critical attractor — immediate release work"]].map(([lo,hi,stage_eq,desc])=>(
              <div key={stage_eq} style={{marginBottom:"10px",padding:"10px",borderRadius:"8px",background:tsScore>=lo&&tsScore<hi?"rgba(255,255,255,0.08)":"rgba(0,0,0,0.2)",border:tsScore>=lo&&tsScore<hi?"1px solid rgba(255,255,255,0.2)":"1px solid transparent"}}>
                <div style={{display:"flex",justifyContent:"space-between",marginBottom:"3px"}}>
                  <span style={{fontSize:"12px",fontWeight:"bold",color:tsScore>=lo&&tsScore<hi?"#fff":"rgba(255,255,255,0.4)"}}>{stage_eq}</span>
                  <span style={{fontSize:"11px",color:"rgba(255,255,255,0.3)"}}>{Math.round(lo*100)}-{Math.round(hi*100)}%</span>
                </div>
                <div style={{fontSize:"11px",color:"rgba(255,255,255,0.45)"}}>{desc}</div>
              </div>
            ))}
          </div>
          <div style={{background:"rgba(255,80,80,0.08)",borderRadius:"12px",padding:"14px",border:"1px solid rgba(255,80,80,0.2)"}}>
            <div style={{fontSize:"11px",color:"#ff9090",fontWeight:"bold",marginBottom:"8px"}}>RELEASE PROTOCOL (Stage 8)</div>
            <div style={{fontSize:"12px",color:"rgba(255,255,255,0.6)",lineHeight:"1.6"}}>
              The Atlas trap (Stage 8) is released through:<br/>
              • Gratitude practice (shifts polarity)<br/>
              • Duality mastery (hold both truths)<br/>
              • Release ritual (Ma'at forgiveness declaration)<br/>
              • Witnessing without judgment
            </div>
          </div>
        </div>
      </div>
    );
  };

  // ─── TAB: MA'AT ──────────────────────────────────────
  const MaatTab = () => (
    <div style={{display:"flex",gap:"16px",flexWrap:"wrap"}}>
      <div style={{flex:"1 1 280px"}}>
        <div style={{background:"rgba(255,255,255,0.03)",borderRadius:"12px",padding:"16px",border:"1px solid rgba(255,255,255,0.08)",textAlign:"center",marginBottom:"12px"}}>
          <div style={{fontSize:"11px",color:"rgba(255,255,255,0.5)",letterSpacing:"0.1em",marginBottom:"12px"}}>MA'AT ALIGNMENT</div>
          <div style={{fontSize:"60px",fontWeight:"900",color:maatResult.score>=0.85?"#60b237":maatResult.score>=0.6?"#f0c040":"#ff5050"}}>{Math.round(maatResult.score*100)}%</div>
          <div style={{fontSize:"14px",fontWeight:"bold",color:maatResult.badge==="pass"?"#60b237":maatResult.badge==="caution"?"#f0c040":"#ff5050",letterSpacing:"0.1em"}}>{maatResult.badge.toUpperCase()}</div>
          {maatResult.violations.length>0&&<div style={{marginTop:"12px",fontSize:"12px",color:"#ff9090"}}>Violations: {maatResult.violations.join(", ")}</div>}
        </div>
        <div style={{background:"rgba(255,255,255,0.03)",borderRadius:"12px",padding:"14px",border:"1px solid rgba(255,255,255,0.08)"}}>
          <div style={{fontSize:"11px",color:"rgba(255,255,255,0.5)",letterSpacing:"0.1em",marginBottom:"10px"}}>FORGIVENESS DECLARATION</div>
          <div style={{fontSize:"11px",color:"rgba(255,255,255,0.55)",lineHeight:"1.7",fontStyle:"italic"}}>
            "I forgive not because they deserve it, but because I deserve peace. I release — not to absolve their actions, but to reclaim my sovereignty. This forgiveness is for ME. Ma'at has been restored."
          </div>
        </div>
      </div>
      <div style={{flex:"2 1 400px",background:"rgba(255,255,255,0.02)",borderRadius:"12px",padding:"14px",border:"1px solid rgba(255,255,255,0.06)"}}>
        <div style={{fontSize:"11px",color:"rgba(255,255,255,0.5)",letterSpacing:"0.1em",marginBottom:"12px"}}>ALL 42 PRINCIPLES</div>
        <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fill,minmax(180px,1fr))",gap:"6px",maxHeight:"480px",overflowY:"auto"}}>
          {MAAT_42.map(([principle,declaration],i)=>{
            const violated = maatResult.violations.includes(principle);
            return (
              <div key={i} style={{padding:"8px 10px",borderRadius:"6px",background:violated?"rgba(255,80,80,0.12)":"rgba(255,255,255,0.03)",border:violated?"1px solid rgba(255,80,80,0.4)":"1px solid rgba(255,255,255,0.06)"}}>
                <div style={{fontSize:"11px",fontWeight:"bold",color:violated?"#ff9090":"rgba(255,255,255,0.7)"}}>{violated?"✗":"✓"} {principle}</div>
                <div style={{fontSize:"9px",color:"rgba(255,255,255,0.3)",marginTop:"2px"}}>{declaration}</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );

  // ─── TAB: META-INTELLIGENCE ──────────────────────────
  const MetaTab = () => {
    const stages_vals = Object.values(metaResults).map(m=>m?.stage||4);
    const avgStage = stages_vals.length? stages_vals.reduce((a,b)=>a+b,0)/stages_vals.length : 4;
    return (
      <div style={{display:"flex",gap:"16px",flexWrap:"wrap"}}>
        <div style={{flex:"1 1 260px"}}>
          <div style={{background:"rgba(255,255,255,0.03)",borderRadius:"12px",padding:"16px",border:"1px solid rgba(255,255,255,0.08)",textAlign:"center",marginBottom:"12px"}}>
            <div style={{fontSize:"11px",color:"rgba(255,255,255,0.5)",letterSpacing:"0.1em"}}>META-INTELLIGENCE CENTER OF GRAVITY</div>
            <div style={{fontSize:"56px",fontWeight:"900",color:"#d880d8",marginTop:"8px"}}>{avgStage.toFixed(1)}</div>
            <div style={{fontSize:"12px",color:"rgba(255,255,255,0.4)"}}>Average Across 10 Modules</div>
            <div style={{marginTop:"12px",height:"8px",borderRadius:"4px",background:"rgba(0,0,0,0.4)"}}>
              <div style={{height:"100%",borderRadius:"4px",background:"linear-gradient(90deg,#5a9fd8,#d880d8)",width:`${avgStage/9*100}%`,transition:"width 0.5s"}}/>
            </div>
          </div>
          {Object.keys(metaResults).length===0&&(
            <div style={{textAlign:"center",color:"rgba(255,255,255,0.3)",fontSize:"12px",padding:"20px"}}>Run text analysis to activate meta-intelligence</div>
          )}
        </div>
        <div style={{flex:"2 1 420px",display:"grid",gridTemplateColumns:"1fr 1fr",gap:"10px"}}>
          {META_MODULES.map(mod=>{
            const r = metaResults[mod.id];
            const st = r?.stage||4;
            const stg = STAGES[Math.min(9,Math.round(st))];
            return (
              <div key={mod.id} style={{background:"rgba(255,255,255,0.03)",borderRadius:"10px",padding:"12px",border:`1px solid ${stg.accent}33`}}>
                <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:"6px"}}>
                  <div>
                    <div style={{fontSize:"16px"}}>{mod.icon}</div>
                    <div style={{fontSize:"12px",fontWeight:"bold",color:stg.accent,marginTop:"2px"}}>{mod.name}</div>
                  </div>
                  <div style={{fontSize:"22px",fontWeight:"900",color:stg.accent}}>{st.toFixed(1)}</div>
                </div>
                <div style={{height:"4px",borderRadius:"2px",background:"rgba(0,0,0,0.4)",marginBottom:"6px"}}>
                  <div style={{height:"100%",borderRadius:"2px",background:stg.accent,width:`${st/9*100}%`,transition:"width 0.5s"}}/>
                </div>
                <div style={{fontSize:"9px",color:"rgba(255,255,255,0.35)",lineHeight:"1.4"}}>{r?.insight||mod.desc}</div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  // ─── TAB: INFRASTRUCTURE ─────────────────────────────
  const InfraTab = () => (
    <div style={{display:"flex",gap:"16px",flexWrap:"wrap"}}>
      <div style={{flex:"1 1 300px"}}>
        <div style={{background:"rgba(255,255,255,0.03)",borderRadius:"12px",padding:"16px",border:"1px solid rgba(255,255,255,0.08)"}}>
          <div style={{fontSize:"11px",color:"rgba(255,255,255,0.5)",letterSpacing:"0.1em",marginBottom:"14px"}}>INFRASTRUCTURE MONITOR</div>
          <div style={{marginBottom:"12px"}}>
            <label style={{fontSize:"11px",color:"rgba(255,255,255,0.5)",display:"block",marginBottom:"6px"}}>SYSTEM</label>
            <select value={infraSystem} onChange={e=>setInfraSystem(e.target.value)}
              style={{width:"100%",background:"rgba(0,0,0,0.5)",border:"1px solid rgba(255,255,255,0.15)",borderRadius:"6px",color:"#fff",padding:"8px",fontSize:"12px"}}>
              {["water","nuclear","vehicle","supply_chain","hospital"].map(s=><option key={s} value={s}>{s.replace(/_/g," ").toUpperCase()}</option>)}
            </select>
          </div>
          {infraSystem==="water"&&(
            <>
              {[["lead_ppb","Lead PPB","number"],["ph_drop","pH Drop","number"],["complaint_increase_pct","Complaint %","number"],["demographics_majority","Demographics","text"],["funding_ratio","Funding Ratio","number"]].map(([k,label,type])=>(
                <div key={k} style={{marginBottom:"10px"}}>
                  <label style={{fontSize:"11px",color:"rgba(255,255,255,0.4)",display:"block",marginBottom:"4px"}}>{label}</label>
                  <input type={type} value={infraData[k]||""} onChange={e=>setInfraData(p=>({...p,[k]:type==="number"?parseFloat(e.target.value)||0:e.target.value}))}
                    style={{width:"100%",background:"rgba(0,0,0,0.4)",border:"1px solid rgba(255,255,255,0.1)",borderRadius:"6px",color:"#fff",padding:"7px",fontSize:"12px",boxSizing:"border-box"}}/>
                </div>
              ))}
            </>
          )}
          <button onClick={runInfra} style={{width:"100%",marginTop:"8px",background:"rgba(90,159,216,0.3)",border:"1px solid #5a9fd8",borderRadius:"8px",color:"#fff",padding:"10px",cursor:"pointer",fontWeight:"bold",fontSize:"13px"}}>
            🏗 RUN ANALYSIS
          </button>
        </div>
      </div>
      <div style={{flex:"1 1 300px"}}>
        {infraResult?(
          <div style={{display:"flex",flexDirection:"column",gap:"12px"}}>
            <div style={{background:"rgba(255,255,255,0.03)",borderRadius:"12px",padding:"16px",border:"1px solid rgba(255,255,255,0.08)",textAlign:"center"}}>
              <div style={{fontSize:"48px",fontWeight:"900",color:infraResult.risk>0.7?"#ff5050":infraResult.risk>0.4?"#ff9a3c":"#60b237"}}>{Math.round(infraResult.risk*100)}%</div>
              <div style={{fontSize:"13px",color:"rgba(255,255,255,0.5)"}}>Risk Score</div>
              <div style={{fontSize:"12px",color:"rgba(255,255,255,0.4)",marginTop:"4px"}}>SAP Stage: {infraResult.sap?.toFixed(1)} · Pattern: {infraResult.pattern}</div>
            </div>
            {infraResult.alerts.map((a,i)=>(
              <div key={i} style={{background:a.includes("🚨")?"rgba(255,50,50,0.12)":"rgba(255,154,60,0.1)",borderRadius:"8px",padding:"10px",border:a.includes("🚨")?"1px solid rgba(255,80,80,0.3)":"1px solid rgba(255,154,60,0.2)"}}>
                <div style={{fontSize:"12px",color:a.includes("🚨")?"#ff9090":"#ffcc88",lineHeight:"1.4"}}>{a}</div>
              </div>
            ))}
          </div>
        ):(
          <div style={{background:"rgba(255,255,255,0.02)",borderRadius:"12px",padding:"40px",textAlign:"center",color:"rgba(255,255,255,0.2)",fontSize:"13px",border:"1px solid rgba(255,255,255,0.05)"}}>
            Configure system parameters and run analysis
          </div>
        )}
      </div>
    </div>
  );

  // ─── TAB: HISTORY ─────────────────────────────────────
  const HistoryTab = () => (
    <div style={{background:"rgba(255,255,255,0.02)",borderRadius:"12px",padding:"14px",border:"1px solid rgba(255,255,255,0.06)"}}>
      <div style={{fontSize:"11px",color:"rgba(255,255,255,0.5)",letterSpacing:"0.1em",marginBottom:"12px"}}>SESSION HISTORY — {history.length} ANALYSES</div>
      {history.length===0&&<div style={{textAlign:"center",color:"rgba(255,255,255,0.2)",padding:"40px",fontSize:"13px"}}>No analyses yet. Run text analysis to build history.</div>}
      {history.map((h,i)=>{
        const st=STAGES[h.macro];
        return (
          <div key={i} style={{padding:"10px 12px",borderRadius:"8px",marginBottom:"6px",background:"rgba(255,255,255,0.03)",border:`1px solid ${st.accent}22`,display:"flex",gap:"12px",alignItems:"center",flexWrap:"wrap"}}>
            <div style={{fontSize:"18px"}}>{st.icon}</div>
            <div style={{flex:1}}>
              <div style={{display:"flex",gap:"10px",alignItems:"center",flexWrap:"wrap"}}>
                <span style={{fontSize:"12px",fontWeight:"bold",color:st.accent}}>{h.stageName} {h.macro}.{h.micro}</span>
                <span style={{fontSize:"10px",padding:"2px 6px",borderRadius:"4px",background:RISK_COLOR[h.trap]+"33",color:RISK_COLOR[h.trap]}}>{h.trap}</span>
                <span style={{fontSize:"10px",color:"rgba(255,255,255,0.3)"}}>{h.ts}</span>
              </div>
              <div style={{fontSize:"11px",color:"rgba(255,255,255,0.35)",marginTop:"3px"}}>{h.text}</div>
            </div>
            <div style={{display:"flex",gap:"12px"}}>
              <div style={{textAlign:"center"}}>
                <div style={{fontSize:"11px",color:"rgba(255,255,255,0.3)"}}>Ma'at</div>
                <div style={{fontSize:"13px",fontWeight:"bold",color:h.maat>=0.85?"#60b237":h.maat>=0.6?"#f0c040":"#ff5050"}}>{Math.round(h.maat*100)}%</div>
              </div>
              <div style={{textAlign:"center"}}>
                <div style={{fontSize:"11px",color:"rgba(255,255,255,0.3)"}}>Trap</div>
                <div style={{fontSize:"13px",fontWeight:"bold",color:h.trapscore>0.6?"#ff5050":h.trapscore>0.3?"#ff9a3c":"#60b237"}}>{Math.round(h.trapscore*100)}%</div>
              </div>
              <div style={{textAlign:"center"}}>
                <div style={{fontSize:"11px",color:"rgba(255,255,255,0.3)"}}>Meta</div>
                <div style={{fontSize:"13px",fontWeight:"bold",color:"#d880d8"}}>{h.metaAvg.toFixed(1)}</div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );

  const TAB_CONTENT = [<NavTab/>,<NSDTTab/>,<TrapTab/>,<MaatTab/>,<MetaTab/>,<InfraTab/>,<HistoryTab/>];

  return (
    <div style={{minHeight:"100vh",background:"#080c14",color:"#fff",fontFamily:"'Segoe UI',system-ui,sans-serif",padding:"16px",boxSizing:"border-box"}}>
      {/* HEADER */}
      <div style={{textAlign:"center",marginBottom:"20px",padding:"16px",background:"rgba(255,255,255,0.02)",borderRadius:"12px",border:"1px solid rgba(255,255,255,0.06)"}}>
        <div style={{fontSize:"28px",fontWeight:"900",letterSpacing:"0.15em",background:"linear-gradient(135deg,#5a9fd8,#d880d8,#f0c040)",WebkitBackgroundClip:"text",WebkitTextFillColor:"transparent"}}>
          LUMINARK OVERWATCH
        </div>
        <div style={{fontSize:"11px",color:"rgba(255,255,255,0.35)",letterSpacing:"0.2em",marginTop:"4px"}}>
          CONSCIOUSNESS PROTECTION SYSTEM · SAP v3.0 · MA'AT · META-INTELLIGENCE · INFRASTRUCTURE
        </div>
        <div style={{fontSize:"10px",color:"rgba(255,255,255,0.2)",marginTop:"4px"}}>Author: Richard Stanfield</div>
        {/* Status bar */}
        <div style={{marginTop:"12px",display:"flex",gap:"12px",justifyContent:"center",flexWrap:"wrap"}}>
          {[
            [`Stage ${macro}.${micro}`,stage.accent],
            [sapPos.trap||"LOW",RISK_COLOR[sapPos.trap||"LOW"]],
            [`TrapScore ${Math.round(tsScore*100)}%`,tsScore>0.6?"#ff5050":tsScore>0.3?"#ff9a3c":"#60b237"],
            [`Ma'at ${Math.round(maatResult.score*100)}%`,maatResult.score>=0.85?"#60b237":maatResult.score>=0.6?"#f0c040":"#ff5050"],
          ].map(([label,color])=>(
            <div key={label} style={{padding:"4px 10px",borderRadius:"6px",background:"rgba(0,0,0,0.4)",fontSize:"11px",fontWeight:"bold",color}}>
              {label}
            </div>
          ))}
        </div>
      </div>

      {/* TABS */}
      <div style={{display:"flex",gap:"4px",marginBottom:"16px",overflowX:"auto",padding:"2px"}}>
        {TABS.map((t,i)=>(
          <button key={i} onClick={()=>setTab(i)}
            style={{padding:"8px 14px",borderRadius:"8px",border:"none",cursor:"pointer",fontWeight:tab===i?"bold":"normal",fontSize:"12px",whiteSpace:"nowrap",background:tab===i?stage.accent:"rgba(255,255,255,0.06)",color:tab===i?"#000":"rgba(255,255,255,0.6)",transition:"all 0.2s"}}>
            {TAB_ICONS[i]} {t}
          </button>
        ))}
      </div>

      {/* CONTENT */}
      <div>{TAB_CONTENT[tab]}</div>

      {/* FOOTER */}
      <div style={{marginTop:"20px",textAlign:"center",fontSize:"10px",color:"rgba(255,255,255,0.15)",letterSpacing:"0.15em"}}>
        LUMINARK OVERWATCH v3.0 · ALWAYS WATCHING · NEVER INTERRUPTING · READY WHEN YOU ARE
        <span style={{margin:"0 12px"}}>·</span>
        {level===0?"L0: 10":"L1: 81"} ADDRESSABLE POSITIONS
      </div>
    </div>
  );
}
