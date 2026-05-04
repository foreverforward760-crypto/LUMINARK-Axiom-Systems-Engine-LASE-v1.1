import { useState, useEffect, useRef, useCallback } from "react";

// ============================================================
// CONSTANTS — mirrors Python backend exactly
// ============================================================
const USSM = {
  0: { name: "Reactive",       star: "Plenara",  duality: "High Flexibility vs Zero Resilience",            tumble: "Will tumble to Procedural as manual energy exhausts." },
  1: { name: "Procedural",     star: "Algenib",  duality: "Predictable Order vs Extreme Brittleness",       tumble: "Will tumble to Regulated upon novel external shocks." },
  2: { name: "Regulated",      star: "Pherkad",  duality: "Active Stability vs Over-correction Jitter",     tumble: "Will tumble to Adaptive to reduce resource consumption." },
  3: { name: "Adaptive",       star: "Merak",    duality: "High Performance vs Niche-Dependency",           tumble: "Will tumble to Threshold when the niche changes." },
  4: { name: "Foundation",     star: "Dubhe",    duality: "Consolidated Base vs Stagnation Risk",           tumble: "Will tumble to Threshold to seek further growth." },
  5: { name: "Threshold",      star: "Kochab",   duality: "Strategic Foresight vs Model-Reality Drift",     tumble: "POINT OF NO RETURN. Must pivot or escalate." },
  6: { name: "Integrated",     star: "Polaris",  duality: "Peak Synergy vs Lack of Entropy",                tumble: "Will tumble to Scaled as it outgrows its boundaries." },
  7: { name: "Scaled",         star: "Talitha",  duality: "Infrastructure Status vs Decentralized Chaos",   tumble: "Will tumble to Rigidity Risk via over-optimization." },
  8: { name: "Rigidity Risk",  star: "Thuban",   duality: "Peak Efficiency vs Compressed Tension",          tumble: "COLLAPSE IMMINENT. Must deliberately un-learn to return to Stage 5." },
  9: { name: "Meta-Coherent",  star: "Yunus",    duality: "Universal Stability vs Selfish Reversion",       tumble: "Equilibrium maintained unless reverting to Stage 4." },
};

const STAGE_COLORS = {
  0:"#64748b",1:"#0ea5e9",2:"#06b6d4",3:"#10b981",
  4:"#84cc16",5:"#f59e0b",6:"#8b5cf6",7:"#ec4899",
  8:"#ef4444",9:"#f0abfc"
};
const STAGE_ICONS = {
  0:"◎",1:"◈",2:"⟁",3:"✦",4:"⬡",
  5:"⊗",6:"✺",7:"◉",8:"⚠",9:"∞"
};
const TRAP_COLORS = { LOW:"#10b981", ELEVATED:"#f59e0b", HIGH:"#f97316", CRITICAL:"#ef4444" };

const NSDT_CENTROIDS = {
  0:[0,0,0,.1,0],1:[.1,0,.3,.3,0],2:[.2,.1,.4,.2,.1],3:[.3,.4,.2,.2,.3],
  4:[.4,.7,.1,.3,.5],5:[.5,.3,.9,.6,.4],6:[.7,.6,.2,.5,.8],
  7:[.6,.2,.8,.85,.3],8:[.8,.8,.1,.8,.9],9:[.9,.5,.3,.95,.7]
};

const META_MODULES = [
  ["paradox","⟳","Paradox"],["myth","⚔","Myth"],["emotion","♥","Emotion"],
  ["temporal","◷","Temporal"],["geometry","✦","Geometry"],["liminality","◈","Liminality"],
  ["linguistic","✎","Linguistic"],["somatic","◎","Somatic"],["emergence","✺","Emergence"],
  ["metacognition","∞","MetaCognition"]
];

const TRICKSTERS = {
  Coyote:      "Glued feathers to fly. Fell in a cactus. Lesson: You can't skip stages.",
  Anansi:      "Tricked the gods for all the stories. Lesson: Narrative frame beats brute force.",
  Loki:        "Cut Sif's hair, panicked, accidentally created Thor's hammer. Lesson: Chaos creates.",
  "Br'er Rabbit":"Begged not to be thrown in the briar patch — where he lives. Lesson: Use perceived weakness as strength.",
  Eshu:        "Wears a hat red on one side, white on the other. Lesson: Both things are true."
};

function euclidean(a, b) { return Math.sqrt(a.reduce((s,v,i)=>s+(v-b[i])**2,0)); }

function assessNSDT(vec) {
  const v = [vec.complexity, vec.stability, vec.tension, vec.adaptability, vec.coherence];
  const dists = {};
  for (let s = 0; s <= 9; s++) dists[s] = euclidean(v, NSDT_CENTROIDS[s]);
  const best = Object.entries(dists).reduce((a,b) => a[1]<b[1]?a:b)[0];
  const bestD = dists[best], maxD = Math.max(...Object.values(dists));
  const confidence = 1.0 - (bestD / (maxD + 1e-9));
  const micro = Math.max(0, Math.min(9, Math.round(vec.tension*5 + (1-vec.coherence)*5)));
  const nano  = Math.max(0, Math.min(9, Math.round(vec.adaptability*9)));
  const pico  = Math.max(0, Math.min(9, Math.round(vec.complexity*9)));
  const stage = parseInt(best);
  let trapRisk = "LOW";
  if (stage===8 && vec.adaptability<0.4) trapRisk="CRITICAL";
  else if (stage>=7 && vec.tension<0.2)  trapRisk="HIGH";
  else if (stage===5)                     trapRisk="ELEVATED";
  return { stage, micro, nano, pico, confidence: parseFloat(confidence.toFixed(3)), trapRisk,
           fractalAddress:`${stage}.${micro}.${nano}.${pico}`, ussm: USSM[stage], distances: dists };
}

function calcTrapscore(S, R, A) { return parseFloat((S * R * (1 - A)).toFixed(3)); }

function textToNSDT(text) {
  const tl = text.toLowerCase(), words = tl.split(/\s+/), wc = words.length;
  const avg = words.reduce((s,w)=>s+w.length,0)/Math.max(wc,1);
  const score = (kws, base=0.05) => Math.min(1, base + kws.filter(k=>tl.includes(k)).length*0.12);
  return {
    complexity:   Math.max(0.1, Math.min(1, (avg/8)*0.4+(wc/100)*0.3+score(["complex","system","multiple","layers","deep","fractal","network","infrastructure"])*0.3)),
    stability:    score(["stable","certain","confident","secure","steady","solid","perfect","guaranteed","absolute","100%","proven"]),
    tension:      score(["anxious","uncertain","conflict","stress","fear","crisis","urgent","breaking","threshold","critical","pivot"]),
    adaptability: score(["flexible","adapt","change","adjust","pivot","creative","explore","navigate","switch","both","simultaneously","learn"]),
    coherence:    score(["coherent","clear","aligned","unified","integrated","whole","complete","perfect","harmony","mission","purpose"])
  };
}

function maatValidate(text) {
  const tl = text.toLowerCase();
  const principles = [
    ["Truth",["lie","false","deceive","mislead","fake"]],
    ["Non-arrogance",["absolute","perfect","infallible","guaranteed","100%","impossible to fail"]],
    ["Non-violence",["crush","force","attack","eliminate","kill"]],
    ["Non-deceit",["scam","trick","manipulate","hide","conceal"]],
    ["Non-coercion",["force","compel","coerce","demand"]],
    ["Justice",["unfair","unjust","bias","discriminate"]],
    ["Harmony",["destroy","disrupt","chaos"]],
  ];
  const violations = principles.filter(([,kws])=>kws.some(k=>tl.includes(k))).map(([p])=>p);
  const score = Math.max(0, 100 - violations.length*14.3);
  return { score: parseFloat(score.toFixed(1)), badge: score>=78?"PASS":score>=55?"CAUTION":"FAIL", violations };
}

function metaIntelligence(text) {
  const tl = text.toLowerCase();
  const get = (kws) => kws.filter(k=>tl.includes(k)).length;
  const paradox   = Math.min(9, get(["both","simultaneously","yet","paradox","balance","duality","contradiction"])*1.2);
  const myth      = ["call","threshold","ordeal","reward","return","resurrection"].reduce((mx,k,i)=>tl.includes(k)?Math.max(mx,[1.5,5,6.5,7,8.5,9][i]):mx,0);
  const emotions  = {joy:7,grief:4,anger:3,fear:2,hope:6,shame:2,love:8,awe:9};
  const found     = Object.entries(emotions).filter(([k])=>tl.includes(k)).map(([,v])=>v);
  const emotion   = found.length ? found.reduce((s,v)=>s+v,0)/found.length : 0;
  const horizons  = {cosmological:9,generational:7,decade:5.5,year:4,month:3,week:2,now:5};
  const temporal  = Object.entries(horizons).reduce((mx,[k,v])=>tl.includes(k)?Math.max(mx,v):mx,3);
  const geometry  = Object.entries({fractal:9,spiral:7,mandala:8,lattice:6,void:.5,linear:3}).reduce((mx,[k,v])=>tl.includes(k)?Math.max(mx,v):mx,3);
  const limhits   = ["between","neither","not yet","crossing","in-between","threshold","transition"].filter(k=>tl.includes(k)).length;
  const liminality= Math.min(8, 4.5 + limhits*0.5);
  const vmeme     = {beige:1.5,purple:2,red:2.5,blue:3.5,orange:5,green:6,yellow:7.5,turquoise:8.5};
  const linguistic= Object.entries(vmeme).reduce((mx,[k,v])=>tl.includes(k)?Math.max(mx,v):mx,4);
  const somatic   = Object.entries({ventral:8,vagal:7,sympathetic:3,dorsal:1,mobilized:6,grounded:7}).reduce((mx,[k,v])=>tl.includes(k)?Math.max(mx,v):mx,4);
  const emhits    = ["tipping point","critical mass","breakthrough","suddenly","phase transition"].filter(k=>tl.includes(k)).length;
  const emergence = Math.min(9, 3 + emhits*1.5);
  const mhits     = ["i notice","i observe","zooming out","multiple perspectives","stepping back","meta","recursive"].filter(k=>tl.includes(k)).length;
  const metacognition = Math.min(9, 4+mhits*0.7);
  const vals = {paradox,myth,emotion,temporal,geometry,liminality,linguistic,somatic,emergence,metacognition};
  const avg = Object.values(vals).reduce((s,v)=>s+v,0)/10;
  const leading = Object.entries(vals).reduce((a,b)=>a[1]>b[1]?a:b)[0];
  return { modules: vals, avg: parseFloat(avg.toFixed(2)), leading };
}

function yunusCheck(text, stageHistory) {
  const tl = text.toLowerCase();
  const arroganceKw = ["absolute","undeniable","100%","impossible to fail","guaranteed","perfect","risk-free","cannot fail","infallible"];
  const cfKw = ["what if","worst-case","failure mode","edge case","assumption","contingency","risk","unless","however","except"];
  const arrogance = arroganceKw.filter(k=>tl.includes(k)).length;
  const cf = cfKw.filter(k=>tl.includes(k)).length;
  let score = 100, flags = [];
  if (arrogance > 0) {
    score = Math.max(0, score - arrogance*(cf===0?15:5));
    if (stageHistory.length>0 && stageHistory[stageHistory.length-1]>=7 && cf===0) {
      flags.push("🚨 STAGE 8 RIGIDITY TRAP: Hyper-confidence without counterfactuals detected.");
    } else {
      flags.push(`Arrogance markers detected (${arrogance}). Epistemic humility compromised.`);
    }
  }
  const recent = stageHistory.slice(-5);
  const stuckHigh = recent.filter(s=>s>=7).length >= 3;
  if (stuckHigh) {
    score = Math.min(score, 40);
    flags.push("🔴 YUNUS TRAJECTORY ALARM: Sustained high-stage occupancy detected. Behavioral pattern, not snapshot.");
  }
  return { score: parseFloat(score.toFixed(1)), trap: score<50||stuckHigh, flags };
}

function consensusConfidence(vec) {
  const evalWeights = [[2,1,1.5,1,1.5],[1,2,1,1.5,2],[1.5,1.5,2,2,1]];
  const v = [vec.complexity,vec.stability,vec.tension,vec.adaptability,vec.coherence];
  const votes = evalWeights.map(w=>{
    const wv = v.map((x,i)=>x*w[i]);
    const mx = Math.max(...w);
    const norm = wv.map(x=>x/mx);
    const dists = {};
    for(let s=0;s<=9;s++) dists[s]=euclidean(norm,NSDT_CENTROIDS[s]);
    return parseInt(Object.entries(dists).reduce((a,b)=>a[1]<b[1]?a:b)[0]);
  });
  const majority = votes.reduce((acc,v)=>{acc[v]=(acc[v]||0)+1;return acc;},{});
  const majorityStage = parseInt(Object.entries(majority).reduce((a,b)=>parseInt(a[1])>parseInt(b[1])?a:b)[0]);
  const agreement = votes.filter(v=>v===majorityStage).length/3;
  return {
    votes, majorityStage, agreement: parseFloat((agreement*100).toFixed(0)),
    label: agreement===1?"HIGH CONSENSUS":agreement<0.5?"SPLIT VERDICT":"MODERATE CONSENSUS",
    uncertainty: parseFloat((1-agreement).toFixed(2))
  };
}

// ============================================================
// SMALL COMPONENTS
// ============================================================
const Badge = ({text, color="#10b981"}) => (
  <span style={{background:`${color}22`,color,border:`1px solid ${color}44`,
    padding:"2px 8px",borderRadius:4,fontSize:11,fontFamily:"monospace",fontWeight:700}}>
    {text}
  </span>
);

const Gauge = ({value, size=120, color="#f59e0b", label=""}) => {
  const pct = Math.max(0, Math.min(100, value));
  const r = (size/2)-10, cx = size/2, cy = size/2;
  const circ = 2*Math.PI*r, dash = (pct/100)*circ*0.75;
  return (
    <div style={{textAlign:"center"}}>
      <svg width={size} height={size} style={{transform:"rotate(-135deg)"}}>
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="#1e293b" strokeWidth={8}
          strokeDasharray={`${circ*0.75} ${circ*0.25}`} strokeLinecap="round"/>
        <circle cx={cx} cy={cy} r={r} fill="none" stroke={color} strokeWidth={8}
          strokeDasharray={`${dash} ${circ-dash}`} strokeLinecap="round"
          style={{transition:"stroke-dasharray 0.5s ease"}}/>
      </svg>
      <div style={{marginTop:-size*0.4,fontSize:size*0.18,fontWeight:800,color,fontFamily:"monospace"}}>
        {Math.round(pct)}%
      </div>
      {label && <div style={{fontSize:10,color:"#64748b",marginTop:4}}>{label}</div>}
    </div>
  );
};

const PulseBar = ({value, max=9, color="#8b5cf6", label=""}) => (
  <div style={{marginBottom:8}}>
    <div style={{display:"flex",justifyContent:"space-between",marginBottom:3}}>
      <span style={{fontSize:11,color:"#94a3b8"}}>{label}</span>
      <span style={{fontSize:11,color,fontFamily:"monospace",fontWeight:700}}>
        {typeof value==="number"?value.toFixed(1):value}
      </span>
    </div>
    <div style={{background:"#1e293b",borderRadius:4,height:6,overflow:"hidden"}}>
      <div style={{width:`${(value/max)*100}%`,height:"100%",background:`linear-gradient(90deg,${color}88,${color})`,
        borderRadius:4,transition:"width 0.4s ease"}}/>
    </div>
  </div>
);

const NSDTSlider = ({label, value, onChange, color}) => (
  <div style={{marginBottom:14}}>
    <div style={{display:"flex",justifyContent:"space-between",marginBottom:6}}>
      <span style={{fontSize:12,color:"#94a3b8"}}>{label}</span>
      <span style={{fontSize:12,color,fontFamily:"monospace",fontWeight:700}}>{(value*100).toFixed(0)}%</span>
    </div>
    <div style={{position:"relative",height:6,background:"#1e293b",borderRadius:3}}>
      <div style={{position:"absolute",left:0,top:0,height:"100%",width:`${value*100}%`,
        background:`linear-gradient(90deg,${color}66,${color})`,borderRadius:3,transition:"width 0.2s"}}/>
      <input type="range" min="0" max="100" value={Math.round(value*100)}
        onChange={e=>onChange(parseInt(e.target.value)/100)}
        style={{position:"absolute",top:-7,left:0,width:"100%",opacity:0,cursor:"pointer",height:20}}/>
    </div>
  </div>
);

// ============================================================
// STAGE GRID (81-cell fractal)
// ============================================================
function StageGrid({currentStage, currentMicro, trapHistory, thresholdCells, onSelect}) {
  const cells = [];
  for (let macro=0;macro<=8;macro++) {
    for (let micro=0;micro<=8;micro++) {
      const isCurrent = macro===currentStage && micro===currentMicro;
      const isTrap = trapHistory.some(([m,n])=>m===macro&&n===micro);
      const isThreshold = macro===5;
      const color = STAGE_COLORS[macro];
      cells.push(
        <div key={`${macro}-${micro}`}
          onClick={()=>onSelect&&onSelect(macro,micro)}
          title={`Stage ${macro}.${micro} — ${USSM[macro].name}`}
          style={{
            width:36,height:36,borderRadius:4,cursor:"pointer",
            display:"flex",alignItems:"center",justifyContent:"center",fontSize:9,
            fontFamily:"monospace",fontWeight:700,
            background: isCurrent ? color : isTrap ? "#ef444433" : isThreshold ? "#f59e0b11" : "#0f172a",
            border: isCurrent ? `2px solid ${color}` : isTrap ? "1px solid #ef444466" : isThreshold ? "1px solid #f59e0b44" : "1px solid #1e293b",
            color: isCurrent ? "#fff" : color+"99",
            boxShadow: isCurrent ? `0 0 12px ${color}88` : "none",
            transition:"all 0.2s"
          }}>
          {isCurrent ? STAGE_ICONS[macro] : `${macro}.${micro}`}
        </div>
      );
    }
  }
  return (
    <div style={{display:"grid",gridTemplateColumns:"repeat(9,36px)",gap:3}}>
      {cells}
    </div>
  );
}

// ============================================================
// SPHERICAL COORDINATE VISUALIZER
// ============================================================
function SphericalViz({theta, phi, radius=1}) {
  const cx=60, cy=60, r=45;
  const projX = cx + r * Math.sin(theta||0) * Math.cos(phi||0);
  const projY = cy - r * Math.cos(theta||0) * 0.6;
  return (
    <svg width={120} height={120} style={{overflow:"visible"}}>
      <ellipse cx={cx} cy={cy} rx={r} ry={r*0.35} fill="none" stroke="#1e293b" strokeWidth={1}/>
      <line x1={cx} y1={cy-r} x2={cx} y2={cy+r} stroke="#1e293b" strokeWidth={1}/>
      <line x1={cx-r} y1={cy} x2={cx+r} y2={cy} stroke="#1e293b" strokeWidth={1}/>
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="#0f172a" strokeWidth={12}/>
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="#1e293b" strokeWidth={1}/>
      <line x1={cx} y1={cy} x2={projX} y2={projY} stroke="#8b5cf6" strokeWidth={2}/>
      <circle cx={projX} cy={projY} r={5} fill="#8b5cf6" style={{filter:"drop-shadow(0 0 6px #8b5cf6)"}}/>
      <text x={cx} y={cy+r+14} textAnchor="middle" fill="#475569" fontSize={9} fontFamily="monospace">
        θ:{(theta||0).toFixed(2)} φ:{(phi||0).toFixed(2)}
      </text>
    </svg>
  );
}

// ============================================================
// TRAJECTORY CHART
// ============================================================
function TrajectoryChart({stageHistory}) {
  if (!stageHistory?.length) return <div style={{color:"#475569",fontSize:12,textAlign:"center",padding:20}}>No history yet</div>;
  const w=280, h=80, pad=20;
  const pts = stageHistory.map((s,i)=>[
    pad + (i/(Math.max(stageHistory.length-1,1)))*(w-pad*2),
    h - pad - (s/9)*(h-pad*2)
  ]);
  const path = pts.map((p,i)=>`${i===0?"M":"L"}${p[0]},${p[1]}`).join(" ");
  return (
    <svg width={w} height={h}>
      {[0,3,6,9].map(s=>(
        <line key={s} x1={pad} y1={h-pad-(s/9)*(h-pad*2)} x2={w-pad} y2={h-pad-(s/9)*(h-pad*2)}
          stroke="#1e293b" strokeWidth={1} strokeDasharray="3,3"/>
      ))}
      <path d={path} fill="none" stroke="#8b5cf6" strokeWidth={2}
        style={{filter:"drop-shadow(0 0 4px #8b5cf688)"}}/>
      {pts.map((p,i)=>(
        <circle key={i} cx={p[0]} cy={p[1]} r={3}
          fill={STAGE_COLORS[stageHistory[i]]} stroke="#0a0f1e" strokeWidth={1}/>
      ))}
    </svg>
  );
}

// ============================================================
// MAIN APP
// ============================================================
export default function LuminarkApp() {
  const [tab, setTab] = useState("navigator");
  const [text, setText] = useState("");
  const [domain, setDomain] = useState("general");
  const [nsdt, setNsdt] = useState({ complexity:.5, stability:.5, tension:.5, adaptability:.5, coherence:.5 });
  const [ts, setTs] = useState({ S:.5, R:.5, A:.5 });
  const [cultural, setCultural] = useState({ code_switching:false, historical_trauma:false, systemic_oppression:false, multilingual:false, diaspora:false });
  const [hrv, setHrv] = useState({ sdnn:50, rmssd:40, use:false });
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [stageHistory, setStageHistory] = useState([]);
  const [trapHistory, setTrapHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const runAnalysis = useCallback(() => {
    setLoading(true);
    setTimeout(() => {
      const vec = hrv.use
        ? {complexity: Math.min(1,.5+(1-hrv.rmssd/80)*.2), stability:Math.min(1,hrv.sdnn/100),
           tension: Math.max(0,1-hrv.rmssd/80), adaptability:Math.max(0,(1-(1-hrv.rmssd/80))*.8),
           coherence: Math.min(1,hrv.sdnn/100)}
        : text ? textToNSDT(text) : nsdt;

      const nsdtResult = assessNSDT(vec);
      let stage = nsdtResult.stage;

      // Cultural adjustment
      let cultAdj = 0;
      const cultNotes = [];
      if (cultural.code_switching) { cultAdj+=2; cultNotes.push("Code-switching → Stage 6 mastery"); }
      if (cultural.historical_trauma) { cultAdj+=1.5; cultNotes.push("Historical trauma → adaptive vigilance"); }
      if (cultural.systemic_oppression) { cultAdj+=.75; cultNotes.push("Systemic factors separated"); }
      if (cultural.multilingual) { cultAdj+=.5; cultNotes.push("Multilingual complexity recognized"); }
      if (cultural.diaspora) { cultAdj+=.5; cultNotes.push("Diaspora navigation recognized"); }
      stage = Math.min(9, stage + Math.round(cultAdj));

      const trapScore = calcTrapscore(ts.S, ts.R, ts.A);
      const maat = maatValidate(text);
      const meta = metaIntelligence(text);
      const yunus = yunusCheck(text, stageHistory);
      const consensus = consensusConfidence(vec);

      // Spherical coords
      const micro = nsdtResult.micro, nano = nsdtResult.nano, pico = nsdtResult.pico;
      let theta=0, phi=0;
      [[stage,.9],[micro,.1],[nano,.01],[pico,.001]].forEach(([v,w])=>{
        theta += (v*(Math.PI/9))*w;
        phi   += (v*(2*Math.PI/9))*w;
      });

      // Defense
      const threat = Math.max(1-(maat.score/100), yunus.trap?.0.8:0, stageHistory.filter(s=>s>=7).length/Math.max(stageHistory.length,1));
      let defense, defDesc;
      if (yunus.trap||threat>.8)        { defense="🛡️ HARROWING"; defDesc="Forced rewrite initiated. Extracting essence from collapse."; }
      else if (threat>.9)               { defense="🚨 FULL QUARANTINE"; defDesc="Maximum containment. Emergency protocols active."; }
      else if (threat>.75)              { defense="🍄 MYCELIAL CONTAINMENT"; defDesc="Spore walls active. Fragment preservation in progress."; }
      else if (threat>.5)               { defense="🐙 OCTO-CAMOUFLAGE"; defDesc="Void mimicry engaged. Identity concealed from threat."; }
      else                              { defense="🟢 NOMINAL"; defDesc="All systems stable. Monitoring active."; }

      // Wisdom
      const tricksterMap = {
        0:"Coyote",1:"Coyote",2:"Coyote",3:"Br'er Rabbit",4:"Br'er Rabbit",
        5:"Eshu",6:"Anansi",7:"Anansi",8:"Loki",9:"Loki"
      };
      const trickster = tricksterMap[stage];

      const overall = parseFloat(((maat.score/100)*0.4 + (1-stage/9*0.5)*0.25 + Math.min(1,.5+cultAdj*.1)*0.15 + (meta.avg/9)*0.2)*100).toFixed(1);
      const badge = overall>=78?"PASS":overall>=55?"CAUTION":"FAIL";

      const recs = [];
      if (nsdtResult.trapRisk==="CRITICAL") recs.push("⚠️ STAGE 8 TRAP: Practice gratitude + Ma'at forgiveness to release polarity.");
      if (yunus.trap) recs.push("🔴 YUNUS: Trajectory intervention required. Introduce deliberate variability now.");
      if (maat.badge==="FAIL") recs.push("⚖️ MA'AT: Ethical violations detected. Address before proceeding.");
      if (meta.avg<3) recs.push("🧠 META: Expand temporal horizon and paradox capacity.");
      if (!recs.length) recs.push("✅ System operating within healthy parameters.");

      const newResult = {
        stage, micro, nano, pico, fractalAddress:`${stage}.${micro}.${nano}.${pico}`,
        vec, nsdt:nsdtResult, trapRisk:nsdtResult.trapRisk, trapScore, maat, meta, yunus,
        consensus, cultAdj, cultNotes, defense, defDesc, trickster,
        tricksterLesson: TRICKSTERS[trickster], ussm: USSM[stage], overall, badge, recs,
        theta, phi, confidence: nsdtResult.confidence,
        stage8release: (stage>=7||nsdtResult.trapRisk==="CRITICAL")?
          ["Practice gratitude to release polarity compression",
           "Embrace duality — hold both truths simultaneously",
           "Ma'at forgiveness declaration",
           "Step into Stage 9: witness without judgment"]:null,
        timestamp: new Date().toLocaleTimeString()
      };

      setResult(newResult);
      const newStageHistory = [...stageHistory, stage].slice(-20);
      setStageHistory(newStageHistory);
      if (nsdtResult.trapRisk==="CRITICAL"||nsdtResult.trapRisk==="HIGH") {
        setTrapHistory(prev=>[...prev,[stage,micro]].slice(-10));
      }
      setHistory(prev=>[newResult,...prev].slice(-30));
      setLoading(false);
    }, 300);
  }, [text, nsdt, ts, cultural, hrv, stageHistory]);

  const stageColor = result ? STAGE_COLORS[result.stage] : "#8b5cf6";

  // ── TABS ──
  const TABS = [
    {id:"navigator",label:"🔭 Navigator"},
    {id:"nsdt",label:"🧬 NSDT"},
    {id:"trapscore",label:"⚠ TrapScore"},
    {id:"maat",label:"⚖ Ma'at"},
    {id:"meta",label:"🧠 Meta-Intel"},
    {id:"consensus",label:"⟁ Consensus"},
    {id:"history",label:"📜 History"},
  ];

  const S={
    app:{minHeight:"100vh",background:"#040810",color:"#e2e8f0",fontFamily:"'Courier New',monospace",userSelect:"none"},
    header:{background:"linear-gradient(135deg,#0a0f1e,#0f172a)",borderBottom:"1px solid #1e293b",padding:"16px 24px"},
    headerTitle:{fontSize:22,fontWeight:900,letterSpacing:3,background:`linear-gradient(90deg,${stageColor},#8b5cf6,#06b6d4)`,
      WebkitBackgroundClip:"text",WebkitTextFillColor:"transparent"},
    statusBar:{display:"flex",gap:16,padding:"8px 24px",background:"#040810",borderBottom:"1px solid #0f172a",flexWrap:"wrap"},
    tabBar:{display:"flex",gap:1,background:"#0a0f1e",borderBottom:"1px solid #1e293b",overflowX:"auto"},
    tab:(active)=>({padding:"10px 16px",fontSize:12,fontWeight:700,cursor:"pointer",border:"none",
      background:active?"#0f172a":"transparent",color:active?"#e2e8f0":"#475569",
      borderBottom:active?`2px solid ${stageColor}`:"2px solid transparent",letterSpacing:1,whiteSpace:"nowrap"}),
    content:{padding:24,maxWidth:1100,margin:"0 auto"},
    card:{background:"#0a0f1e",border:"1px solid #1e293b",borderRadius:8,padding:20,marginBottom:16},
    grid2:{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16},
    grid3:{display:"grid",gridTemplateColumns:"1fr 1fr 1fr",gap:12},
    label:{fontSize:11,color:"#475569",letterSpacing:2,marginBottom:8,display:"block"},
    bigNum:(color)=>({fontSize:36,fontWeight:900,color,fontFamily:"monospace",lineHeight:1}),
    input:{width:"100%",background:"#0f172a",border:"1px solid #1e293b",borderRadius:6,
      padding:"10px 14px",color:"#e2e8f0",fontSize:13,resize:"vertical",fontFamily:"inherit",boxSizing:"border-box"},
    btn:{padding:"10px 24px",background:`linear-gradient(135deg,${stageColor},#8b5cf6)`,border:"none",
      borderRadius:6,color:"#fff",fontSize:13,fontWeight:700,cursor:"pointer",letterSpacing:1,
      opacity:loading?0.6:1},
    select:{background:"#0f172a",border:"1px solid #1e293b",borderRadius:6,padding:"8px 12px",
      color:"#e2e8f0",fontSize:12,cursor:"pointer"},
    check:(active)=>({display:"flex",alignItems:"center",gap:8,padding:"8px 12px",borderRadius:6,cursor:"pointer",
      background:active?"#1e293b":"transparent",border:`1px solid ${active?stageColor:"#1e293b"}`,marginBottom:4}),
  };

  return (
    <div style={S.app}>
      {/* HEADER */}
      <div style={S.header}>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",flexWrap:"wrap",gap:8}}>
          <div>
            <div style={S.headerTitle}>LUMINARK OVERWATCH PRIME</div>
            <div style={{fontSize:10,color:"#475569",letterSpacing:2,marginTop:2}}>
              v8.0 · RICHARD L. STANFIELD · MERIDIAN AXIOM ALIGNMENT TECHNOLOGIES
            </div>
          </div>
          {result && (
            <div style={{display:"flex",gap:8,flexWrap:"wrap"}}>
              <Badge text={result.ussm.star} color={stageColor}/>
              <Badge text={`STAGE ${result.stage} ${result.ussm.name.toUpperCase()}`} color={stageColor}/>
              <Badge text={result.badge} color={result.badge==="PASS"?"#10b981":result.badge==="CAUTION"?"#f59e0b":"#ef4444"}/>
            </div>
          )}
        </div>
      </div>

      {/* STATUS BAR */}
      {result && (
        <div style={S.statusBar}>
          <div style={{display:"flex",alignItems:"center",gap:6}}>
            <span style={{fontSize:18,color:stageColor}}>{STAGE_ICONS[result.stage]}</span>
            <span style={{fontSize:11,fontWeight:700,color:stageColor}}>{result.fractalAddress}</span>
          </div>
          <div style={{fontSize:11,color:"#475569"}}>
            TRAP: <span style={{color:TRAP_COLORS[result.trapRisk],fontWeight:700}}>{result.trapRisk}</span>
          </div>
          <div style={{fontSize:11,color:"#475569"}}>
            TRAPSCORE: <span style={{color:result.trapScore>0.6?"#ef4444":result.trapScore>0.4?"#f59e0b":"#10b981",fontWeight:700}}>
              {(result.trapScore*100).toFixed(1)}%
            </span>
          </div>
          <div style={{fontSize:11,color:"#475569"}}>
            MA'AT: <span style={{color:"#8b5cf6",fontWeight:700}}>{result.maat.score}%</span>
          </div>
          <div style={{fontSize:11,color:"#475569"}}>
            CONSENSUS: <span style={{color:"#06b6d4",fontWeight:700}}>{result.consensus.label}</span>
          </div>
          <div style={{fontSize:11,color:"#475569"}}>
            DEFENSE: <span style={{color:"#f59e0b",fontWeight:700}}>{result.defense}</span>
          </div>
          <div style={{fontSize:11,color:"#475569"}}>
            OVERALL: <span style={{color:result.badge==="PASS"?"#10b981":result.badge==="CAUTION"?"#f59e0b":"#ef4444",fontWeight:700}}>
              {result.overall}%
            </span>
          </div>
        </div>
      )}

      {/* TABS */}
      <div style={S.tabBar}>
        {TABS.map(t=>(
          <button key={t.id} style={S.tab(tab===t.id)} onClick={()=>setTab(t.id)}>{t.label}</button>
        ))}
      </div>

      {/* CONTENT */}
      <div style={S.content}>

        {/* ── NAVIGATOR TAB ── */}
        {tab==="navigator" && (
          <div style={S.grid2}>
            <div>
              <div style={S.card}>
                <span style={S.label}>TEXT INPUT — NATURAL LANGUAGE ANALYSIS</span>
                <textarea value={text} onChange={e=>setText(e.target.value)} rows={5} style={S.input}
                  placeholder="Enter text to analyze... The system will extract NSDT vectors, detect stage, run Ma'at validation, Meta-Intelligence, and all modules."/>
                <div style={{display:"flex",gap:12,marginTop:12,flexWrap:"wrap",alignItems:"center"}}>
                  <select value={domain} onChange={e=>setDomain(e.target.value)} style={S.select}>
                    {["general","business","projects","trading","environmental","finance"].map(d=>(
                      <option key={d} value={d}>{d.toUpperCase()}</option>
                    ))}
                  </select>
                  <button style={S.btn} onClick={runAnalysis} disabled={loading}>
                    {loading?"SCANNING...":"⚡ RUN FULL ANALYSIS"}
                  </button>
                </div>
              </div>

              {/* Cultural context */}
              <div style={S.card}>
                <span style={S.label}>CULTURAL INTELLIGENCE — CORRECTION FACTORS</span>
                {Object.entries(cultural).map(([key,val])=>(
                  <div key={key} style={S.check(val)} onClick={()=>setCultural(p=>({...p,[key]:!p[key]}))}>
                    <div style={{width:14,height:14,borderRadius:3,border:`2px solid ${val?stageColor:"#475569"}`,
                      background:val?stageColor:"transparent",transition:"all 0.2s"}}/>
                    <span style={{fontSize:11,color:val?"#e2e8f0":"#64748b"}}>
                      {key.replace(/_/g," ").toUpperCase()}
                      {val&&<span style={{color:stageColor,marginLeft:6}}>+{
                        key==="code_switching"?"2.0":key==="historical_trauma"?"1.5":key==="systemic_oppression"?"0.75":"0.5"
                      } stage adj</span>}
                    </span>
                  </div>
                ))}
              </div>

              {/* HRV */}
              <div style={S.card}>
                <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:12}}>
                  <span style={S.label}>POLYVAGAL / HRV BRIDGE</span>
                  <div style={S.check(hrv.use)} onClick={()=>setHrv(p=>({...p,use:!p.use}))}
                    style={{...S.check(hrv.use),padding:"4px 10px",marginBottom:0}}>
                    <span style={{fontSize:11,color:hrv.use?"#10b981":"#64748b"}}>USE HRV</span>
                  </div>
                </div>
                {hrv.use && (
                  <>
                    <NSDTSlider label={`SDNN (ms) — ${hrv.sdnn}`} value={hrv.sdnn/100}
                      onChange={v=>setHrv(p=>({...p,sdnn:v*100}))} color="#10b981"/>
                    <NSDTSlider label={`RMSSD (ms) — ${hrv.rmssd}`} value={hrv.rmssd/100}
                      onChange={v=>setHrv(p=>({...p,rmssd:v*100}))} color="#0ea5e9"/>
                    <div style={{fontSize:10,color:"#475569",marginTop:6}}>
                      Compatible with Apple Watch HealthKit, Polar H10, Garmin, Oura Ring
                    </div>
                  </>
                )}
              </div>
            </div>

            <div>
              {result ? (
                <>
                  {/* Current position card */}
                  <div style={{...S.card,border:`1px solid ${stageColor}44`,background:`linear-gradient(135deg,#0a0f1e,${stageColor}08)`}}>
                    <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start"}}>
                      <div>
                        <div style={{fontSize:48,color:stageColor,lineHeight:1}}>{STAGE_ICONS[result.stage]}</div>
                        <div style={S.bigNum(stageColor)}>{result.fractalAddress}</div>
                        <div style={{fontSize:14,color:"#94a3b8",marginTop:4}}>{result.ussm.name} · ★ {result.ussm.star}</div>
                        <div style={{fontSize:11,color:"#475569",marginTop:4,maxWidth:260}}>{result.ussm.duality}</div>
                      </div>
                      <SphericalViz theta={result.theta} phi={result.phi}/>
                    </div>
                    <div style={{marginTop:12,padding:"8px 12px",background:"#0f172a",borderRadius:6,
                      fontSize:11,color:"#f59e0b",fontStyle:"italic"}}>
                      ⚠ {result.ussm.tumble}
                    </div>

                    {/* Trajectory chart */}
                    {stageHistory.length>1 && (
                      <div style={{marginTop:12}}>
                        <span style={{fontSize:10,color:"#475569",letterSpacing:2}}>TRAJECTORY</span>
                        <div style={{marginTop:6}}>
                          <TrajectoryChart stageHistory={stageHistory}/>
                        </div>
                      </div>
                    )}

                    {result.cultAdj>0 && (
                      <div style={{marginTop:10,padding:"8px 12px",background:"#0f172a",borderRadius:6}}>
                        <div style={{fontSize:10,color:"#475569",letterSpacing:2,marginBottom:4}}>CULTURAL CORRECTIONS APPLIED</div>
                        {result.cultNotes.map((n,i)=><div key={i} style={{fontSize:11,color:"#0ea5e9"}}>✓ {n}</div>)}
                        <div style={{fontSize:11,color:"#10b981",marginTop:4}}>Total adjustment: +{result.cultAdj.toFixed(2)} stages</div>
                      </div>
                    )}
                  </div>

                  {/* Defense */}
                  <div style={{...S.card,border:`1px solid ${result.defense.includes("QUARANTINE")?"#ef4444":result.defense.includes("HARROW")?"#f59e0b":"#1e293b"}44`}}>
                    <span style={S.label}>BIO-DEFENSE STATUS</span>
                    <div style={{fontSize:16,fontWeight:700,marginBottom:4}}>{result.defense}</div>
                    <div style={{fontSize:12,color:"#64748b"}}>{result.defDesc}</div>
                  </div>

                  {/* Wisdom */}
                  <div style={S.card}>
                    <span style={S.label}>TRICKSTER PEDAGOGY</span>
                    <div style={{fontSize:13,fontWeight:700,color:stageColor,marginBottom:4}}>
                      [{result.trickster}]
                    </div>
                    <div style={{fontSize:12,color:"#94a3b8",fontStyle:"italic",marginBottom:8}}>
                      "{result.tricksterLesson}"
                    </div>
                    {result.stage8release && (
                      <div style={{padding:"10px 12px",background:"#0f172a",borderRadius:6}}>
                        <div style={{fontSize:10,color:"#ef4444",letterSpacing:2,marginBottom:6}}>STAGE 8 RELEASE PROTOCOL</div>
                        {result.stage8release.map((p,i)=><div key={i} style={{fontSize:11,color:"#94a3b8",marginBottom:3}}>→ {p}</div>)}
                      </div>
                    )}
                  </div>

                  {/* Recommendations */}
                  <div style={S.card}>
                    <span style={S.label}>RECOMMENDATIONS</span>
                    {result.recs.map((r,i)=>(
                      <div key={i} style={{fontSize:12,color:"#e2e8f0",padding:"6px 10px",background:"#0f172a",
                        borderRadius:6,marginBottom:6,borderLeft:`3px solid ${stageColor}`}}>{r}</div>
                    ))}
                  </div>
                </>
              ) : (
                <div style={{...S.card,textAlign:"center",padding:60}}>
                  <div style={{fontSize:48,marginBottom:16}}>◉</div>
                  <div style={{fontSize:14,color:"#475569"}}>Enter text and run analysis to begin</div>
                  <div style={{fontSize:11,color:"#334155",marginTop:8}}>
                    LUMINARK OVERWATCH PRIME v8.0<br/>
                    Always Watching · Never Interrupting · Ready When You Are
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ── STAGE GRID ── */}
        {tab==="navigator" && (
          <div style={S.card}>
            <span style={S.label}>81-STAGE FRACTAL NAVIGATOR (9×9 GRID)</span>
            <StageGrid
              currentStage={result?.stage??-1}
              currentMicro={result?.micro??-1}
              trapHistory={trapHistory}
              onSelect={(m,n)=>{}}
            />
            <div style={{display:"flex",gap:16,marginTop:12,fontSize:11}}>
              <span style={{color:"#ef4444"}}>■ TRAP CELL</span>
              <span style={{color:"#f59e0b"}}>■ THRESHOLD</span>
              <span style={{color:stageColor}}>■ CURRENT</span>
            </div>
          </div>
        )}

        {/* ── NSDT TAB ── */}
        {tab==="nsdt" && (
          <div style={S.grid2}>
            <div style={S.card}>
              <span style={S.label}>NSDT VECTOR — 5 DIMENSIONS</span>
              {[["complexity","#8b5cf6"],["stability","#10b981"],["tension","#f59e0b"],
                ["adaptability","#06b6d4"],["coherence","#ec4899"]].map(([k,c])=>(
                <NSDTSlider key={k} label={k.toUpperCase()} value={nsdt[k]}
                  onChange={v=>setNsdt(p=>({...p,[k]:v}))} color={c}/>
              ))}
              <button style={S.btn} onClick={runAnalysis}>⚡ ASSESS STAGE</button>
            </div>
            <div>
              {result && (
                <>
                  <div style={S.card}>
                    <span style={S.label}>STAGE MATCH</span>
                    <div style={S.bigNum(stageColor)}>{result.stage}.{result.micro}</div>
                    <div style={{fontSize:13,color:"#94a3b8",marginTop:4}}>{result.ussm.name}</div>
                    <div style={{marginTop:8}}>
                      <Badge text={`${(result.confidence*100).toFixed(0)}% CONFIDENCE`} color={stageColor}/>
                    </div>
                  </div>
                  <div style={S.card}>
                    <span style={S.label}>EUCLIDEAN DISTANCES TO ALL 10 STAGES</span>
                    {Object.entries(result.nsdt.distances||{}).sort((a,b)=>a[1]-b[1]).map(([s,d])=>(
                      <div key={s} style={{marginBottom:6}}>
                        <div style={{display:"flex",justifyContent:"space-between",marginBottom:2}}>
                          <span style={{fontSize:11,color:STAGE_COLORS[parseInt(s)]}}>
                            {STAGE_ICONS[parseInt(s)]} Stage {s} {USSM[parseInt(s)].name}
                          </span>
                          <span style={{fontSize:11,fontFamily:"monospace",color:"#64748b"}}>{d.toFixed(4)}</span>
                        </div>
                        <div style={{height:4,background:"#0f172a",borderRadius:2}}>
                          <div style={{width:`${Math.max(4,(1-d/2)*100)}%`,height:"100%",
                            background:STAGE_COLORS[parseInt(s)],borderRadius:2}}/>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {/* ── TRAPSCORE TAB ── */}
        {tab==="trapscore" && (
          <div style={S.grid2}>
            <div style={S.card}>
              <span style={S.label}>TRAPSCORE FORMULA: S × R × (1−A)</span>
              {[["S","Severity",ts.S,"#ef4444"],["R","Rigidity",ts.R,"#f97316"],["A","Adaptability",ts.A,"#10b981"]].map(([k,label,val,c])=>(
                <NSDTSlider key={k} label={`${k} — ${label} (${(val*100).toFixed(0)}%)`}
                  value={val} onChange={v=>setTs(p=>({...p,[k]:v}))} color={c}/>
              ))}
              <div style={{padding:"12px 16px",background:"#0f172a",borderRadius:8,textAlign:"center",marginTop:12}}>
                <div style={{fontSize:13,color:"#475569",marginBottom:4}}>S × R × (1−A)</div>
                <div style={{fontFamily:"monospace",fontSize:22,fontWeight:700,color:"#f59e0b"}}>
                  {ts.S.toFixed(2)} × {ts.R.toFixed(2)} × {(1-ts.A).toFixed(2)} = <span style={{color:
                    calcTrapscore(ts.S,ts.R,ts.A)>0.6?"#ef4444":calcTrapscore(ts.S,ts.R,ts.A)>0.4?"#f97316":"#10b981"}}>
                    {(calcTrapscore(ts.S,ts.R,ts.A)*100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
            <div>
              <div style={S.card}>
                <Gauge value={calcTrapscore(ts.S,ts.R,ts.A)*100} size={160}
                  color={calcTrapscore(ts.S,ts.R,ts.A)>0.6?"#ef4444":calcTrapscore(ts.S,ts.R,ts.A)>0.4?"#f97316":"#10b981"}
                  label="TRAPSCORE"/>
                <div style={{textAlign:"center",marginTop:8}}>
                  {[["0-25%","Stages 0-4","#10b981","FREE"],["25-50%","Stage 5","#f59e0b","WATCH"],
                    ["50-75%","Stage 7-8","#f97316","TRAPPED"],["75-100%","Stage 8 LOCK","#ef4444","CRITICAL LOCK"]].map(([r,s,c,l])=>(
                    <div key={r} style={{display:"flex",justifyContent:"space-between",fontSize:11,padding:"4px 12px",
                      background:"#0f172a",borderRadius:4,marginBottom:3}}>
                      <span style={{color:"#64748b"}}>{r}</span>
                      <span style={{color:"#475569"}}>{s}</span>
                      <span style={{color:c,fontWeight:700}}>{l}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ── MA'AT TAB ── */}
        {tab==="maat" && (
          <div style={S.grid2}>
            <div style={S.card}>
              <span style={S.label}>MA'AT 42 PRINCIPLES — ETHICAL VALIDATION</span>
              {result ? (
                <>
                  <Gauge value={result.maat.score} size={140}
                    color={result.maat.badge==="PASS"?"#10b981":result.maat.badge==="CAUTION"?"#f59e0b":"#ef4444"}
                    label="MA'AT ALIGNMENT"/>
                  <div style={{textAlign:"center",marginTop:8}}>
                    <Badge text={result.maat.badge}
                      color={result.maat.badge==="PASS"?"#10b981":result.maat.badge==="CAUTION"?"#f59e0b":"#ef4444"}/>
                  </div>
                  {result.maat.violations.length>0 && (
                    <div style={{marginTop:16}}>
                      <span style={S.label}>VIOLATIONS DETECTED</span>
                      {result.maat.violations.map((v,i)=>(
                        <div key={i} style={{fontSize:12,color:"#ef4444",padding:"6px 10px",
                          background:"#0f172a",borderRadius:4,marginBottom:4}}>
                          ✗ {v}
                        </div>
                      ))}
                    </div>
                  )}
                  {result.maat.violations.length===0 && (
                    <div style={{marginTop:12,fontSize:12,color:"#10b981"}}>
                      ✓ All monitored principles aligned
                    </div>
                  )}
                </>
              ) : (
                <div style={{color:"#475569",fontSize:12,padding:20}}>Run analysis to validate Ma'at alignment</div>
              )}
            </div>
            <div style={S.card}>
              <span style={S.label}>PRINCIPLES REFERENCE</span>
              <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:4}}>
                {["Truth","Justice","Harmony","Balance","Order","Righteousness","Compassion",
                  "Non-violence","Non-stealing","Non-deceit","Non-arrogance","Non-coercion",
                  "Gratitude","Patience","Humility","Service","Courage","Wisdom",
                  "Discernment","Integrity","Forgiveness","Accountability"].map(p=>(
                  <div key={p} style={{fontSize:10,padding:"4px 8px",background:"#0f172a",borderRadius:3,
                    color: result?.maat?.violations?.includes(p)?"#ef4444":"#475569",
                    border:`1px solid ${result?.maat?.violations?.includes(p)?"#ef444433":"#0f172a"}`}}>
                    {result?.maat?.violations?.includes(p)?"✗":"✓"} {p}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ── META-INTELLIGENCE TAB ── */}
        {tab==="meta" && result && (
          <>
            <div style={{...S.card,textAlign:"center",display:"inline-block",marginBottom:16,padding:"16px 32px"}}>
              <span style={S.label}>META-INTELLIGENCE CENTER OF GRAVITY</span>
              <div style={S.bigNum("#8b5cf6")}>{result.meta.avg.toFixed(2)}</div>
              <div style={{fontSize:12,color:"#475569",marginTop:4}}>
                LEADING: <span style={{color:"#8b5cf6",fontWeight:700}}>{result.meta.leading.toUpperCase()}</span>
              </div>
            </div>
            <div style={S.grid2}>
              {META_MODULES.map(([key, icon, label])=>{
                const val = result.meta.modules[key]||0;
                const c = STAGE_COLORS[Math.min(9,Math.max(0,Math.round(val)))];
                return (
                  <div key={key} style={{...S.card,borderColor:`${c}22`}}>
                    <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:8}}>
                      <span style={{fontSize:18,color:c}}>{icon}</span>
                      <span style={{fontSize:12,color:"#64748b"}}>{label}</span>
                      <span style={{fontSize:16,fontWeight:800,color:c,fontFamily:"monospace"}}>
                        {val.toFixed(1)}
                      </span>
                    </div>
                    <div style={{height:6,background:"#0f172a",borderRadius:3}}>
                      <div style={{width:`${(val/9)*100}%`,height:"100%",
                        background:`linear-gradient(90deg,${c}66,${c})`,borderRadius:3}}/>
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        )}
        {tab==="meta" && !result && (
          <div style={{...S.card,color:"#475569",textAlign:"center",padding:40}}>Run analysis to see Meta-Intelligence modules</div>
        )}

        {/* ── CONSENSUS TAB ── */}
        {tab==="consensus" && result && (
          <div style={S.grid2}>
            <div style={S.card}>
              <span style={S.label}>EVALUATOR CONSENSUS</span>
              <div style={{fontSize:36,fontWeight:900,fontFamily:"monospace",color:"#06b6d4",marginBottom:8}}>
                {result.consensus.agreement}%
              </div>
              <Badge text={result.consensus.label} color={result.consensus.agreement===100?"#10b981":result.consensus.agreement<50?"#ef4444":"#f59e0b"}/>
              <div style={{marginTop:16}}>
                {[["Risk-Sensitive",0],["Stability-Sensitive",1],["Adaptability-Sensitive",2]].map(([name,i])=>(
                  <div key={i} style={{display:"flex",justifyContent:"space-between",padding:"8px 12px",
                    background:"#0f172a",borderRadius:4,marginBottom:4,fontSize:12}}>
                    <span style={{color:"#64748b"}}>{name}</span>
                    <span style={{color:STAGE_COLORS[result.consensus.votes[i]],fontWeight:700}}>
                      Stage {result.consensus.votes[i]} — {USSM[result.consensus.votes[i]].name}
                    </span>
                  </div>
                ))}
              </div>
              <div style={{marginTop:12,padding:"10px 12px",background:"#0f172a",borderRadius:6}}>
                <div style={{fontSize:11,color:"#475569",marginBottom:4}}>UNCERTAINTY METRIC</div>
                <div style={{fontSize:22,fontWeight:700,fontFamily:"monospace",
                  color:result.consensus.uncertainty>0.3?"#ef4444":"#10b981"}}>
                  {(result.consensus.uncertainty*100).toFixed(0)}%
                </div>
                <div style={{fontSize:11,color:"#475569",marginTop:4}}>
                  {result.consensus.uncertainty===0?"All evaluators agree — high confidence signal.":
                   result.consensus.uncertainty>0.5?"Evaluators disagree significantly — increase data before acting.":
                   "Moderate disagreement — treat stage reading with appropriate caution."}
                </div>
              </div>
            </div>
            <div>
              <div style={S.card}>
                <span style={S.label}>YUNUS PROTOCOL STATUS</span>
                <div style={{fontSize:24,fontWeight:700,fontFamily:"monospace",
                  color:result.yunus.trap?"#ef4444":"#10b981",marginBottom:8}}>
                  {result.yunus.trap?"⚠ TRIGGERED":"✓ CLEAR"}
                </div>
                <div style={{fontSize:16,fontWeight:700,color:"#94a3b8",marginBottom:12}}>
                  Score: {result.yunus.score}%
                </div>
                {result.yunus.flags.length>0 ? result.yunus.flags.map((f,i)=>(
                  <div key={i} style={{fontSize:11,color:"#f59e0b",padding:"8px 10px",
                    background:"#0f172a",borderRadius:4,marginBottom:4,borderLeft:"3px solid #f59e0b"}}>{f}</div>
                )) : (
                  <div style={{fontSize:12,color:"#10b981"}}>No epistemic risk markers detected.</div>
                )}
              </div>
              <div style={S.card}>
                <span style={S.label}>TRAJECTORY STATE</span>
                <div style={{marginBottom:12}}>
                  <TrajectoryChart stageHistory={stageHistory}/>
                </div>
                {stageHistory.length>1 && (
                  <div style={{display:"flex",gap:8,flexWrap:"wrap"}}>
                    <Badge text={`${stageHistory.length} READINGS`} color="#475569"/>
                    <Badge text={`AVG STAGE: ${(stageHistory.reduce((s,v)=>s+v,0)/stageHistory.length).toFixed(1)}`} color="#8b5cf6"/>
                    <Badge text={`CURRENT: ${stageHistory[stageHistory.length-1]}`} color={stageColor}/>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
        {tab==="consensus" && !result && (
          <div style={{...S.card,color:"#475569",textAlign:"center",padding:40}}>Run analysis to see consensus data</div>
        )}

        {/* ── HISTORY TAB ── */}
        {tab==="history" && (
          <div>
            {history.length===0 ? (
              <div style={{...S.card,color:"#475569",textAlign:"center",padding:40}}>No history yet. Run analyses to see them here.</div>
            ) : history.map((h,i)=>(
              <div key={i} style={{...S.card,marginBottom:8}}>
                <div style={{display:"flex",gap:12,alignItems:"center",flexWrap:"wrap"}}>
                  <span style={{fontSize:20,color:STAGE_COLORS[h.stage]}}>{STAGE_ICONS[h.stage]}</span>
                  <div>
                    <div style={{fontSize:12,fontWeight:700,color:STAGE_COLORS[h.stage]}}>
                      {h.fractalAddress} — {h.ussm.name}
                    </div>
                    <div style={{fontSize:11,color:"#475569"}}>{h.timestamp}</div>
                  </div>
                  <div style={{display:"flex",gap:6,flexWrap:"wrap",marginLeft:"auto"}}>
                    <Badge text={h.badge} color={h.badge==="PASS"?"#10b981":h.badge==="CAUTION"?"#f59e0b":"#ef4444"}/>
                    <Badge text={`MA'AT ${h.maat.score}%`} color="#8b5cf6"/>
                    <Badge text={`${h.overall}%`} color={STAGE_COLORS[h.stage]}/>
                    <Badge text={h.trapRisk} color={TRAP_COLORS[h.trapRisk]}/>
                  </div>
                </div>
                {h.input_text && (
                  <div style={{fontSize:11,color:"#334155",marginTop:8,fontStyle:"italic"}}>
                    "{h.input_text?.slice(0,120)}{h.input_text?.length>120?"...":""}"
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* FOOTER */}
      <div style={{textAlign:"center",padding:"20px 24px",color:"#1e293b",fontSize:10,letterSpacing:2,
        borderTop:"1px solid #0f172a",background:"#040810"}}>
        LUMINARK OVERWATCH PRIME v8.0 · MERIDIAN AXIOM ALIGNMENT TECHNOLOGIES<br/>
        ALWAYS WATCHING · NEVER INTERRUPTING · READY WHEN YOU ARE<br/>
        © Richard L. Stanfield · Stanfield's Axiom of Perpetuity · 9¹⁰ = 3,486,784,401 ADDRESSABLE POSITIONS
      </div>
    </div>
  );
}
