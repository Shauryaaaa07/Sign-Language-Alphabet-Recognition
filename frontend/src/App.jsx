import { useState, useEffect, useRef, useCallback } from "react";
import "./App.css";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
const THRESHOLD = 0.75;

// MediaPipe 21 hand landmark connections
const HAND_CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [3, 4],       // Thumb
  [0, 5], [5, 6], [6, 7], [7, 8],       // Index
  [0, 9], [9, 10], [10, 11], [11, 12],   // Middle
  [0, 13], [13, 14], [14, 15], [15, 16], // Ring
  [0, 17], [17, 18], [18, 19], [19, 20], // Pinky
  [5, 9], [9, 13], [13, 17], [0, 17],   // Palm base
];

// Verified numbers from real evaluation
const REPORT = {
  testAcc: 86.34,
  macroF1: 83.96,
  correct: "4,456 / 5,161",
  fusionValAcc: 86.32,
  fusionMacroF1: 82.40,
  landmarkValAcc: 69.17,
  landmarkRfAcc: 77.65,
  versions: [["V1", 56.74], ["V2", 73.1], ["V3", 75.52], ["V4", 77.68], ["V5", 73.81]],
  robust: [["Clean", 80.06], ["Blur", 80.33], ["Tilt +10°", 80.14], ["Low contrast", 57.69], ["High brightness", 47.12], ["Low brightness", 32.82]],
  hard: { W: "0% recall", S: "40% F1", Z: "66.7% F1" },
};

async function predictBlob(blob, mode = "fusion") {
  const fd = new FormData();
  fd.append("file", blob, "frame.jpg");
  const endpoint = mode === "fusion" ? `${API}/models/fusion/predict` : `${API}/predict`;
  const r = await fetch(endpoint, { method: "POST", body: fd });
  if (!r.ok) {
    // If fusion endpoint fails or is unready, fallback to /predict
    if (mode === "fusion") {
      const fallbackR = await fetch(`${API}/predict`, { method: "POST", body: fd });
      if (fallbackR.ok) return fallbackR.json();
    }
    const err = await r.json().catch(() => ({}));
    throw new Error(err.detail || `Server error ${r.status}`);
  }
  return r.json();
}

async function fetchGradCAM(blob) {
  const fd = new FormData();
  fd.append("file", blob, "gradcam.jpg");
  const r = await fetch(`${API}/explain/gradcam?alpha=0.45`, { method: "POST", body: fd });
  if (!r.ok) throw new Error("Grad-CAM generation failed.");
  return r.json();
}

async function fetchQuality(blob) {
  const fd = new FormData();
  fd.append("file", blob, "quality.jpg");
  const r = await fetch(`${API}/vision/quality`, { method: "POST", body: fd });
  if (!r.ok) return null;
  return r.json();
}

async function fetchLandmarks(blob) {
  const fd = new FormData();
  fd.append("file", blob, "landmarks.jpg");
  const r = await fetch(`${API}/vision/landmarks`, { method: "POST", body: fd });
  if (!r.ok) return null;
  return r.json();
}

async function fetchModelComparison(blob) {
  const fd = new FormData();
  fd.append("file", blob, "compare.jpg");
  const r = await fetch(`${API}/models/compare`, { method: "POST", body: fd });
  if (!r.ok) throw new Error("Model comparison failed.");
  return r.json();
}

function useHistory() {
  const [hist, setHist] = useState(() => {
    try { return JSON.parse(localStorage.getItem("signai_hist") || "[]"); } catch { return []; }
  });
  const add = useCallback((e) => setHist((h) => {
    const n = [e, ...h].slice(0, 200);
    try { localStorage.setItem("signai_hist", JSON.stringify(n)); } catch {}
    return n;
  }), []);
  const clear = () => { setHist([]); try { localStorage.removeItem("signai_hist"); } catch {} };
  return { hist, add, clear };
}

function useHealth() {
  const [ok, setOk] = useState(null);
  useEffect(() => {
    let live = true;
    const ping = () => fetch(`${API}/health`).then((r) => live && setOk(r.ok)).catch(() => live && setOk(false));
    ping();
    const t = setInterval(ping, 10000);
    return () => { live = false; clearInterval(t); };
  }, []);
  return ok;
}

const PAGES = [
  ["home", "Home"],
  ["studio", "Studio"],
  ["practice", "Practice"],
  ["models", "Model Lab"],
  ["learn", "Learn A–Z"],
  ["dashboard", "Dashboard"],
  ["performance", "Performance"],
  ["about", "About"],
];

export default function App() {
  const [page, setPage] = useState(() => location.hash.slice(1) || "home");
  const [target, setTarget] = useState(null);
  const h = useHistory();
  const ok = useHealth();

  useEffect(() => {
    const f = () => setPage(location.hash.slice(1) || "home");
    addEventListener("hashchange", f);
    return () => removeEventListener("hashchange", f);
  }, []);

  const go = (p) => {
    location.hash = p;
    window.scrollTo(0, 0);
  };

  return (
    <>
      <header className="bar">
        <a className="brand" href="#home">
          <span className="tile">S</span>SignAI
          <span className="ver">2.0</span>
        </a>
        <nav aria-label="Main">
          {PAGES.map(([k, l]) => (
            <a key={k} href={`#${k}`} aria-current={page === k ? "page" : undefined}>{l}</a>
          ))}
        </nav>
        <span className={`status ${ok === null ? "" : ok ? "up" : "down"}`} role="status">
          {ok === null ? "Checking backend…" : ok ? "Model online" : "Backend offline"}
        </span>
      </header>

      <main>
        {page === "home" && <Home go={go} />}
        {page === "studio" && <Studio h={h} target={target} setTarget={setTarget} />}
        {page === "practice" && <Practice go={go} />}
        {page === "models" && <ModelLab />}
        {page === "learn" && <Learn go={go} setTarget={setTarget} />}
        {page === "dashboard" && <Dashboard h={h} ok={ok} />}
        {page === "performance" && <Performance />}
        {page === "about" && <About />}
      </main>

      <footer>
        SignAI 2.0 Multimodal Research Prototype · ISL Alphabet Recognition A–Z · Educational & Academic Use.
      </footer>
    </>
  );
}

function Home({ go }) {
  const word = "HELLO".split("");
  return (
    <section className="hero">
      <div>
        <h1>Fingerspell. <br />See it turn into voice.</h1>
        <p className="lead">
          Show a hand sign to your camera or upload a photo. Dual AI streams (CNN + 21 MediaPipe Landmarks)
          recognize the letter in real-time, explain decisions with Grad-CAM, and synthesize speech.
        </p>
        <div className="row wrap">
          <button className="btn primary" onClick={() => go("studio")}>Open Studio</button>
          <button className="btn accent" onClick={() => go("practice")}>Practice Mode</button>
          <button className="btn" onClick={() => go("models")}>Model Lab</button>
        </div>
      </div>
      <div className="blocks" aria-label="Example: letters becoming the word HELLO">
        {word.map((c, i) => (
          <span key={i} className="block" style={{ "--i": i }}>{c}</span>
        ))}
        <p>26 Static Alphabet Classes A–Z · Real-Time Multimodal AI</p>
      </div>
      <ol className="steps">
        {[
          ["Capture", "Webcam frame or uploaded photo with optical quality audit"],
          ["MediaPipe", "Extracts 21 3D landmarks & joint angles"],
          ["Dual AI", "Frozen CNN V4 + Landmark Fusion or Pure CNN"],
          ["Explain & Speak", "Grad-CAM visual attribution & browser TTS"],
        ].map(([a, b]) => (
          <li key={a}><b>{a}</b><span>{b}</span></li>
        ))}
      </ol>
    </section>
  );
}

function Studio({ h, target, setTarget }) {
  const [tab, setTab] = useState("camera");
  const [cam, setCam] = useState(false);
  const [busyUI, setBusyUI] = useState(false);
  const [res, setRes] = useState(null);
  const [quality, setQuality] = useState(null);
  const [landmarks, setLandmarks] = useState(null);
  const [showSkeleton, setShowSkeleton] = useState(true);
  const [activeModel, setActiveModel] = useState("fusion"); // "fusion" | "cnn"
  const [err, setErr] = useState("");
  const [text, setText] = useState("");
  const [textHistory, setTextHistory] = useState([]);
  const [speaking, setSpeaking] = useState(false);
  const [state, setState] = useState("idle");
  const [file, setFile] = useState(null);
  const [drag, setDrag] = useState(false);
  const [gradcamModal, setGradcamModal] = useState(null);
  const [loadingGradcam, setLoadingGradcam] = useState(false);

  // Speech Synthesis state
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState("");
  const [speechRate, setSpeechRate] = useState(1.0);
  const [speechPitch, setSpeechPitch] = useState(1.0);

  const v = useRef(), c = useRef(), skelCanvas = useRef(), stream = useRef(), timer = useRef(), busy = useRef(false), buf = useRef([]), lock = useRef(null);

  // Load browser voices
  useEffect(() => {
    if ("speechSynthesis" in window) {
      const loadVoices = () => {
        const vs = window.speechSynthesis.getVoices();
        setVoices(vs);
        if (vs.length && !selectedVoice) {
          const eng = vs.find((v) => v.lang.startsWith("en")) || vs[0];
          setSelectedVoice(eng.name);
        }
      };
      loadVoices();
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }
  }, [selectedVoice]);

  // Draw 21-point hand skeleton on canvas for BOTH hands independently
  const drawSkeleton = useCallback((handsList, width, height) => {
    const cv = skelCanvas.current;
    if (!cv) return;
    cv.width = width;
    cv.height = height;
    const ctx = cv.getContext("2d");
    ctx.clearRect(0, 0, width, height);

    if (!showSkeleton) return;
    const hands = Array.isArray(handsList) ? handsList : (handsList ? [handsList] : []);
    if (!hands.length) return;

    hands.forEach((hand, handIndex) => {
      const lm = hand.landmarks_normalized || hand.landmarks;
      if (!lm || !lm.length) return;

      const isLeft = hand.handedness === "Left";
      // Left Hand: Warm Amber/Orange, Right Hand: Vibrant Sapphire Blue
      const boneColor = isLeft ? "#EA580C" : "#2563EB";
      const jointFill = isLeft ? "#FB923C" : "#60A5FA";
      const tipFill = isLeft ? "#F97316" : "#3B82F6";
      const boxStroke = isLeft ? "rgba(234, 88, 12, 0.85)" : "rgba(37, 99, 235, 0.85)";
      const boxFill = isLeft ? "rgba(234, 88, 12, 0.08)" : "rgba(37, 99, 235, 0.08)";
      const labelBg = isLeft ? "rgba(234, 88, 12, 0.95)" : "rgba(37, 99, 235, 0.95)";

      // 1. Draw Bones
      ctx.strokeStyle = boneColor;
      ctx.lineWidth = 3.2;
      ctx.lineCap = "round";
      ctx.setLineDash([]);

      for (const [i, j] of HAND_CONNECTIONS) {
        if (lm[i] && lm[j]) {
          // Mirrored horizontally: (1 - x) * width
          const x1 = (1 - lm[i].x) * width;
          const y1 = lm[i].y * height;
          const x2 = (1 - lm[j].x) * width;
          const y2 = lm[j].y * height;
          ctx.beginPath();
          ctx.moveTo(x1, y1);
          ctx.lineTo(x2, y2);
          ctx.stroke();
        }
      }

      // 2. Draw Landmark Nodes
      for (let i = 0; i < lm.length; i++) {
        const x = (1 - lm[i].x) * width;
        const y = lm[i].y * height;
        const isTip = [4, 8, 12, 16, 20].includes(i);
        ctx.fillStyle = isTip ? tipFill : jointFill;
        ctx.strokeStyle = "#FFFFFF";
        ctx.lineWidth = 1.8;
        ctx.beginPath();
        ctx.arc(x, y, isTip ? 5.5 : 4.0, 0, 2 * Math.PI);
        ctx.fill();
        ctx.stroke();
      }

      // 3. Draw Independent Bounding Box
      const bbox = hand.bounding_box_normalized || hand.bounding_box;
      if (bbox) {
        const bx1 = (1 - bbox.max_x) * width;
        const by1 = bbox.min_y * height;
        const bw = (bbox.max_x - bbox.min_x) * width;
        const bh = (bbox.max_y - bbox.min_y) * height;

        ctx.save();
        ctx.strokeStyle = boxStroke;
        ctx.fillStyle = boxFill;
        ctx.lineWidth = 2;
        ctx.setLineDash([6, 4]);
        ctx.beginPath();
        if (ctx.roundRect) {
          ctx.roundRect(bx1, by1, bw, bh, 8);
        } else {
          ctx.rect(bx1, by1, bw, bh);
        }
        ctx.fill();
        ctx.stroke();
        ctx.restore();

        // 4. Draw Handedness Label with Overlap Avoidance
        const labelText = `${isLeft ? "LEFT" : "RIGHT"} HAND (${Math.round(hand.confidence * 100)}%)`;
        ctx.font = "bold 11px monospace";
        const textMetrics = ctx.measureText(labelText);
        const textWidth = textMetrics.width;
        const pad = 6;
        const badgeWidth = textWidth + pad * 2;
        const badgeHeight = 22;

        let badgeY = by1 - badgeHeight - 4;
        if (badgeY < 6) {
          badgeY = by1 + 6;
        }
        if (handIndex > 0 && hands[0].bounding_box_normalized) {
          const otherBy = hands[0].bounding_box_normalized.min_y * height;
          if (Math.abs(by1 - otherBy) < 30) {
            badgeY = isLeft ? by1 - badgeHeight - 4 : by1 + bh + 4;
          }
        }

        const badgeX = Math.max(4, Math.min(width - badgeWidth - 4, bx1));

        ctx.save();
        ctx.fillStyle = labelBg;
        ctx.beginPath();
        if (ctx.roundRect) {
          ctx.roundRect(badgeX, badgeY, badgeWidth, badgeHeight, 4);
        } else {
          ctx.rect(badgeX, badgeY, badgeWidth, badgeHeight);
        }
        ctx.fill();

        ctx.fillStyle = "#FFFFFF";
        ctx.textAlign = "left";
        ctx.textBaseline = "middle";
        ctx.fillText(labelText, badgeX + pad, badgeY + badgeHeight / 2);
        ctx.restore();
      }
    });
  }, [showSkeleton]);

  const handle = useCallback((r, fromCam) => {
    setRes(r);
    setErr("");
    h.add({ t: Date.now(), letter: r.predicted_letter, conf: r.confidence, ms: r.inference_time_ms });

    if (!fromCam) return;
    const good = r.confidence >= THRESHOLD ? r.predicted_letter : null;
    buf.current = [...buf.current, good].slice(-3);
    const b = buf.current;
    if (b.length === 3 && b.every((x) => x && x === b[0])) {
      setState("locked");
      if (lock.current !== b[0]) {
        lock.current = b[0];
        setText((t) => {
          setTextHistory((prev) => [...prev, t]);
          return t + b[0];
        });
      }
    } else if (b.every((x) => !x)) {
      lock.current = null;
      setState("idle");
    } else {
      setState("seeing");
    }
  }, [h]);

  const grab = useCallback(async () => {
    const vid = v.current;
    if (busy.current || !vid || !vid.videoWidth) return;
    busy.current = true;
    setBusyUI(true);

    const s = Math.min(vid.videoWidth, vid.videoHeight);
    const cv = c.current;
    cv.width = cv.height = 256;
    cv.getContext("2d").drawImage(vid, (vid.videoWidth - s) / 2, (vid.videoHeight - s) / 2, s, s, 0, 0, 256, 256);

    try {
      const blob = await new Promise((ok) => cv.toBlob(ok, "image/jpeg", 0.9));
      // 1. Run inference
      const pred = await predictBlob(blob, activeModel);
      handle(pred, true);

      // 2. Fetch landmarks for skeleton if enabled
      if (showSkeleton) {
        const lmData = await fetchLandmarks(blob);
        if (lmData && lmData.hands && lmData.hands.length) {
          setLandmarks(lmData.hands);
          drawSkeleton(lmData.hands, vid.clientWidth, vid.clientHeight);
        } else {
          setLandmarks([]);
          drawSkeleton([], vid.clientWidth, vid.clientHeight);
        }
      }

      // 3. Periodic camera quality check
      if (Math.random() < 0.35) {
        const q = await fetchQuality(blob);
        if (q) setQuality(q);
      }
    } catch (e) {
      setErr(e.message || "Could not reach backend on port 8000.");
    } finally {
      busy.current = false;
      setBusyUI(false);
    }
  }, [activeModel, drawSkeleton, handle, showSkeleton]);

  const start = async () => {
    setErr("");
    try {
      stream.current = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 }, audio: false });
      v.current.srcObject = stream.current;
      await v.current.play();
      setCam(true);
      buf.current = [];
      lock.current = null;
      timer.current = setInterval(grab, 700);
    } catch {
      setErr("Camera is blocked or missing. Allow access in your browser or use the Upload tab.");
    }
  };

  const stop = () => {
    clearInterval(timer.current);
    stream.current?.getTracks().forEach((t) => t.stop());
    setCam(false);
    setState("idle");
    setLandmarks(null);
  };

  useEffect(() => stop, []);
  useEffect(() => { if (tab !== "camera" && cam) stop(); }, [tab, cam]);

  const pick = (f) => {
    if (!f) return;
    if (!/^image\/(png|jpe?g)$/.test(f.type)) { setErr("Use a PNG, JPG or JPEG image."); return; }
    setErr("");
    setFile({ f, url: URL.createObjectURL(f) });
  };

  const runUpload = async () => {
    if (!file) return;
    setBusyUI(true);
    try {
      const pred = await predictBlob(file.f, activeModel);
      handle(pred, false);
      const q = await fetchQuality(file.f);
      if (q) setQuality(q);
      const lm = await fetchLandmarks(file.f);
      if (lm && lm.hands && lm.hands.length) {
        setLandmarks(lm.hands);
      } else {
        setLandmarks([]);
      }
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusyUI(false);
    }
  };

  const handleExplainGradcam = async () => {
    setLoadingGradcam(true);
    try {
      let blob;
      if (tab === "camera" && c.current) {
        blob = await new Promise((ok) => c.current.toBlob(ok, "image/jpeg", 0.95));
      } else if (file) {
        blob = file.f;
      }
      if (!blob) throw new Error("No image frame available to explain.");
      const data = await fetchGradCAM(blob);
      setGradcamModal(data);
    } catch (e) {
      setErr(e.message || "Grad-CAM explanation failed.");
    } finally {
      setLoadingGradcam(false);
    }
  };

  // Text builder operations
  const addCurrentLetter = () => {
    if (res && res.confidence >= THRESHOLD) {
      setTextHistory((prev) => [...prev, text]);
      setText((t) => t + res.predicted_letter);
    }
  };
  const addSpace = () => {
    setTextHistory((prev) => [...prev, text]);
    setText((t) => t + " ");
  };
  const handleDelete = () => {
    if (!text) return;
    setTextHistory((prev) => [...prev, text]);
    setText((t) => t.slice(0, -1));
  };
  const handleUndo = () => {
    if (!textHistory.length) return;
    const prev = textHistory[textHistory.length - 1];
    setTextHistory((h) => h.slice(0, -1));
    setText(prev);
  };
  const handleClear = () => {
    setTextHistory((prev) => [...prev, text]);
    setText("");
    lock.current = null;
  };

  // Speech synthesis
  const speak = () => {
    if (!text.trim() || !("speechSynthesis" in window)) return;
    const u = new SpeechSynthesisUtterance(text);
    if (selectedVoice) {
      const vObj = voices.find((v) => v.name === selectedVoice);
      if (vObj) u.voice = vObj;
    }
    u.rate = speechRate;
    u.pitch = speechPitch;
    u.onend = () => setSpeaking(false);
    u.onerror = () => setSpeaking(false);
    setSpeaking(true);
    speechSynthesis.cancel();
    speechSynthesis.speak(u);
  };
  const stopSpeak = () => {
    speechSynthesis.cancel();
    setSpeaking(false);
  };

  const low = res && res.confidence < THRESHOLD;
  const hit = target && res && res.predicted_letter === target && !low;

  return (
    <section className="studio">
      <div className="panel">
        <div className="tabs" role="tablist">
          {[["camera", "Live Camera"], ["upload", "Image Upload"]].map(([k, l]) => (
            <button key={k} role="tab" aria-selected={tab === k} onClick={() => setTab(k)}>{l}</button>
          ))}
        </div>

        {target && (
          <p className="target">
            Practice Target: <b>{target}</b> {hit && <span className="ok">✓ Perfect Match!</span>}{" "}
            <button className="link" onClick={() => setTarget(null)}>End practice</button>
          </p>
        )}

        {/* Model Mode Switcher */}
        <div className="mode-switch" role="group" aria-label="Recognition Engine">
          <button
            className={activeModel === "fusion" ? "active" : ""}
            onClick={() => setActiveModel("fusion")}
          >
            Multimodal Fusion (CNN + Landmarks)
          </button>
          <button
            className={activeModel === "cnn" ? "active" : ""}
            onClick={() => setActiveModel("cnn")}
          >
            CNN V4 Baseline
          </button>
        </div>

        {tab === "camera" ? (
          <>
            <div className={`viewfinder ${state}`}>
              <video ref={v} muted playsInline />
              <canvas ref={skelCanvas} className="skeleton-canvas" />
              <canvas ref={c} className={`cam-feed ${cam ? "" : "hidden"}`} title="AI Crop View (128x128)" />
              {!cam && <p className="empty">Camera offline. Click Start Camera to begin hand tracking.</p>}
              {cam && (
                <div className="hand-count-pill" role="status">
                  <span className={`dot ${landmarks && landmarks.length ? (landmarks.length >= 2 ? "dual" : "single") : "none"}`} />
                  {!landmarks || !landmarks.length
                    ? "0 Hands (Hold in View)"
                    : landmarks.length >= 2
                    ? "2 Hands (Dual Tracking: Left + Right)"
                    : `1 Hand (${landmarks[0].handedness} Hand)`}
                </div>
              )}
              {cam && (
                <span className="hint">
                  {state === "locked" ? "Letter Locked" : state === "seeing" ? "Hold steady…" : "Center hand in box"}
                </span>
              )}
              {cam && <span className="cam-label">AI Input (128×128)</span>}
            </div>

            <div className="row wrap">
              {!cam ? (
                <button className="btn primary" onClick={start}>Start Camera</button>
              ) : (
                <button className="btn" onClick={stop}>Stop Camera</button>
              )}
              <button className="btn" onClick={grab} disabled={!cam || busyUI}>Capture Now</button>
              <label style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: "0.85rem", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={showSkeleton}
                  onChange={(e) => setShowSkeleton(e.target.checked)}
                />
                Hand Skeleton Overlay (21-pt)
              </label>
            </div>
          </>
        ) : (
          <>
            <label
              className={`drop ${drag ? "over" : ""}`}
              onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
              onDragLeave={() => setDrag(false)}
              onDrop={(e) => { e.preventDefault(); setDrag(false); pick(e.dataTransfer.files[0]); }}
            >
              {file ? (
                <img src={file.url} alt="Uploaded sign preview" />
              ) : (
                <span>Drop a hand sign photo here, or click to browse</span>
              )}
              <input type="file" accept="image/png,image/jpeg" hidden onChange={(e) => pick(e.target.files[0])} />
            </label>
            <div className="row wrap">
              <button className="btn primary" onClick={runUpload} disabled={!file || busyUI}>Recognize Letter</button>
            </div>
          </>
        )}

        {/* Real-time Quality Audit Banner */}
        {quality && (
          <div className={`quality-banner ${quality.status === "attention_needed" ? "warn" : ""}`}>
            <div className="metric">
              <b>Quality:</b> {Math.round((quality.quality_score || 0) * 100)}%
              <span className={`badge ${quality.status === "acceptable" ? "ok" : "warn"}`}>
                {quality.status === "acceptable" ? "Optimal" : "Attention"}
              </span>
            </div>
            <div style={{ color: "var(--soft)", fontSize: "0.82rem" }}>
              {quality.primary_advisory || "Lighting and focus good."}
            </div>
          </div>
        )}

        {err && <p className="err" role="alert">{err}</p>}
      </div>

      {/* Output & Text Panel */}
      <div className="panel">
        <div className={`big ${low ? "low" : ""} ${busyUI ? "busy" : ""}`} aria-live="polite">
          <span>{res ? res.predicted_letter : "?"}</span>
        </div>

        {res ? (
          <>
            <p className="conf">
              <b>{(res.confidence * 100).toFixed(1)}%</b> Confidence · {Math.round(res.inference_time_ms ?? 0)} ms
              {res.mode && <span className="badge blue" style={{ marginLeft: 8 }}>{res.mode}</span>}
            </p>
            {low && <p className="warn">Below {THRESHOLD * 100}%: letter will not auto-lock. Align hand in frame.</p>}
            <ul className="top3">
              {(res.top_predictions || []).slice(0, 3).map((p) => (
                <li key={p.letter}>
                  <span>{p.letter}</span>
                  <i style={{ "--w": `${p.confidence * 100}%` }} />
                  <em>{(p.confidence * 100).toFixed(0)}%</em>
                </li>
              ))}
            </ul>

            <div className="row">
              <button
                className="btn accent sm"
                onClick={handleExplainGradcam}
                disabled={loadingGradcam}
              >
                {loadingGradcam ? "Computing Heatmap…" : "Explain Prediction (Grad-CAM)"}
              </button>
            </div>

            {res.dual_hand_analysis && res.dual_hand_analysis.is_dual_hand && (
              <div className="dual-hand-box">
                <h4>
                  <span>Dual-Hand Independent Detection</span>
                  <span className="badge ok">2 Hands Tracked</span>
                </h4>
                <div className="two" style={{ gap: 8, margin: "8px 0" }}>
                  {res.dual_hand_analysis.per_hand_predictions.map((hp, idx) => (
                    <div key={idx} className={`hand-result-card ${hp.handedness.toLowerCase()}`}>
                      <div className="hand-name">{hp.handedness} Hand</div>
                      <div className="hand-letter">{hp.predicted_letter}</div>
                      <div className="hand-conf">{(hp.confidence * 100).toFixed(1)}% Confidence</div>
                    </div>
                  ))}
                </div>
                <p className="notice-text">
                  {res.dual_hand_analysis.notice}
                </p>
              </div>
            )}
          </>
        ) : (
          <p className="tip">Recognized letter, candidate probabilities, and attribution will appear here.</p>
        )}

        <h2>Assembled Text</h2>
        <div className="tiles" aria-label="Recognized text builder">
          {text ? (
            [...text].map((ch, i) => (
              <span key={i} className={ch === " " ? "tile sp" : "tile"}>{ch === " " ? "␣" : ch}</span>
            ))
          ) : (
            <span className="tip">Letters lock in automatically or click Add Letter.</span>
          )}
        </div>

        <div className="row wrap">
          <button className="btn" onClick={addCurrentLetter} disabled={!res || low}>Add Letter</button>
          <button className="btn" onClick={addSpace}>Space</button>
          <button className="btn" onClick={handleDelete} disabled={!text}>Delete</button>
          <button className="btn" onClick={handleUndo} disabled={!textHistory.length}>Undo</button>
          <button className="btn" onClick={handleClear} disabled={!text}>Clear</button>
          <button className="btn" onClick={() => navigator.clipboard?.writeText(text)} disabled={!text}>Copy</button>
        </div>

        {/* Multilingual Speech Controls */}
        <div className="speech-controls">
          <div className="control-row">
            <label style={{ minWidth: 60, fontWeight: 700 }}>Voice:</label>
            <select
              value={selectedVoice}
              onChange={(e) => setSelectedVoice(e.target.value)}
              aria-label="Speech Voice"
            >
              {voices.map((v) => (
                <option key={v.name} value={v.name}>{v.name} ({v.lang})</option>
              ))}
            </select>
          </div>
          <div className="control-row">
            <label style={{ minWidth: 60 }}>Speed ({speechRate}x):</label>
            <input
              type="range"
              min="0.5"
              max="2.0"
              step="0.1"
              value={speechRate}
              onChange={(e) => setSpeechRate(parseFloat(e.target.value))}
              aria-label="Speech Speed"
            />
          </div>
          <div className="control-row">
            <label style={{ minWidth: 60 }}>Pitch ({speechPitch.toFixed(1)}):</label>
            <input
              type="range"
              min="0.5"
              max="1.5"
              step="0.1"
              value={speechPitch}
              onChange={(e) => setSpeechPitch(parseFloat(e.target.value))}
              aria-label="Speech Pitch"
            />
          </div>
          <div className="row wrap" style={{ margin: "6px 0 0" }}>
            {speaking ? (
              <button className="btn primary" onClick={stopSpeak}>Stop Speaking</button>
            ) : (
              <button className="btn primary" onClick={speak} disabled={!text.trim()}>Speak Sentence</button>
            )}
          </div>
        </div>
      </div>

      {/* Grad-CAM Explainability Modal */}
      {gradcamModal && (
        <div className="modal" role="dialog" aria-modal="true" onClick={() => setGradcamModal(null)}>
          <div onClick={(e) => e.stopPropagation()}>
            <h2>Grad-CAM Explainability</h2>
            <p className="tip" style={{ margin: "4px 0 12px" }}>
              Visual attribution for CNN V4 layer <code>{gradcamModal.target_layer_name}</code>
            </p>
            <div className="gradcam-view">
              <div>
                <img src={gradcamModal.heatmap_base64} alt="Heatmap" />
                <span>Salience Heatmap</span>
              </div>
              <div>
                <img src={gradcamModal.overlay_base64} alt="Overlay" />
                <span>Attention Overlay</span>
              </div>
            </div>
            <p style={{ textAlign: "left", fontSize: "0.85rem", color: "var(--soft)", lineHeight: 1.45 }}>
              {gradcamModal.academic_note}
            </p>
            <div className="row" style={{ justifyContent: "center", marginTop: 16 }}>
              <button className="btn primary" onClick={() => setGradcamModal(null)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

function Practice({ go }) {
  const [targetIdx, setTargetIdx] = useState(0);
  const [streak, setStreak] = useState(0);
  const [matched, setMatched] = useState(null);
  const [score, setScore] = useState(0);
  const [evalResult, setEvalResult] = useState(null);
  const [evaluating, setEvaluating] = useState(false);
  const [evalErr, setEvalErr] = useState("");
  const fileInputRef = useRef(null);

  const currentLetter = LETTERS[targetIdx];

  const handleNext = () => {
    setMatched(null);
    setEvalResult(null);
    setEvalErr("");
    setTargetIdx((idx) => (idx + 1) % LETTERS.length);
  };

  const handleRandom = () => {
    setMatched(null);
    setEvalResult(null);
    setEvalErr("");
    setTargetIdx(Math.floor(Math.random() * LETTERS.length));
  };

  const handleReset = () => {
    setStreak(0);
    setScore(0);
    setTargetIdx(0);
    setMatched(null);
    setEvalResult(null);
    setEvalErr("");
  };

  const handleVerifyUpload = async (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    setEvaluating(true);
    setEvalErr("");
    try {
      const pred = await predictBlob(f, "fusion");
      const isMatch = pred.predicted_letter === currentLetter;
      setMatched(isMatch);
      setEvalResult(pred);
      if (isMatch) {
        setStreak((s) => s + 1);
        setScore((sc) => sc + 50);
      } else {
        setStreak(0);
      }
    } catch (err) {
      setEvalErr(err.message || "Failed to analyze practice sign.");
    } finally {
      setEvaluating(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <section>
      <h1 className="h2">Interactive Practice Studio</h1>
      <p className="lead">Test your fingerspelling fluency against verified ISL models with real-time feedback.</p>

      <div className="practice-container">
        <div className="target-card">
          <span className="badge blue">Target Letter</span>
          <div className="target-letter">{currentLetter}</div>
          <Sign l={currentLetter} big />
          <p className="tip">Form this sign clearly in front of your camera or upload a test photo.</p>

          {evalResult && (
            <div style={{ margin: "12px 0", padding: "10px 14px", borderRadius: 8, background: matched ? "rgba(22, 101, 52, 0.08)" : "rgba(180, 83, 9, 0.08)", border: `1px solid ${matched ? "var(--ok)" : "var(--warn)"}` }}>
              <b>{matched ? "✓ Correct Sign Match!" : `✗ Letter Recognized: "${evalResult.predicted_letter}"`}</b>
              <div style={{ fontSize: "0.85rem", color: "var(--soft)", marginTop: 4 }}>
                Confidence: {(evalResult.confidence * 100).toFixed(1)}% · {Math.round(evalResult.inference_time_ms ?? 0)} ms
                {matched ? " · +50 XP Earned" : " · Adjust finger positions to match the reference photo."}
              </div>
            </div>
          )}

          {evalErr && <p className="err" style={{ marginTop: 8 }}>{evalErr}</p>}

          <div className="row wrap" style={{ justifyContent: "center", marginTop: 14 }}>
            <input
              type="file"
              ref={fileInputRef}
              accept="image/png,image/jpeg"
              style={{ display: "none" }}
              onChange={handleVerifyUpload}
            />
            <button
              className="btn primary"
              onClick={() => fileInputRef.current?.click()}
              disabled={evaluating}
            >
              {evaluating ? "Evaluating…" : "Verify Sign Photo"}
            </button>
            <button className="btn" onClick={() => go("studio")}>Live Camera Practice</button>
            <button className="btn" onClick={handleNext}>Next Letter →</button>
            <button className="btn" onClick={handleRandom}>Random Letter</button>
          </div>
        </div>

        <div className="panel">
          <div className="row wrap" style={{ justifyContent: "space-between", alignItems: "center" }}>
            <h2 style={{ margin: 0 }}>Practice Analytics</h2>
            <button className="btn" style={{ fontSize: "0.82rem", padding: "4px 10px" }} onClick={handleReset}>Reset Stats</button>
          </div>
          <div className="three" style={{ margin: "16px 0" }}>
            <div className="panel" style={{ textAlign: "center", padding: 12 }}>
              <div style={{ font: "800 2rem var(--disp)", color: "var(--blue)" }}>{streak}</div>
              <small>Current Streak</small>
            </div>
            <div className="panel" style={{ textAlign: "center", padding: 12 }}>
              <div style={{ font: "800 2rem var(--disp)", color: "var(--ok)" }}>{score}</div>
              <small>Total XP</small>
            </div>
            <div className="panel" style={{ textAlign: "center", padding: 12 }}>
              <div style={{ font: "800 2rem var(--disp)", color: "var(--accent)" }}>{targetIdx + 1}/26</div>
              <small>Progress</small>
            </div>
          </div>

          <h3>Fingerspelling Coaching Tips</h3>
          <ul style={{ paddingLeft: 18, fontSize: "0.92rem", color: "var(--soft)" }}>
            <li>Keep hand parallel to lens; avoid steep vertical tilts.</li>
            <li>Maintain consistent lighting to highlight joint crease lines.</li>
            <li>For signs like <b>B</b> and <b>D</b>, extend fingers fully to allow landmark extraction.</li>
            <li>Letters <b>J</b> and <b>Z</b> naturally incorporate movement trajectories.</li>
          </ul>
        </div>
      </div>
    </section>
  );
}

function ModelLab() {
  const [compResult, setCompResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  const handleUploadCompare = async (e) => {
    const f = e.target.files[0];
    if (!f) return;
    setLoading(true);
    setErr("");
    try {
      const data = await fetchModelComparison(f);
      setCompResult(data);
    } catch (e) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      <h1 className="h2">Model Architecture Laboratory</h1>
      <p className="lead">
        Transparent comparative benchmarks across visual, geometric, multimodal, and temporal ISL classifiers.
      </p>

      <div className="two" style={{ margin: "20px 0" }}>
        <div className="model-card featured">
          <h3>
            Multimodal Fusion Head
            <span className="badge ok">Recommended</span>
          </h3>
          <p className="tip">Two-stream architecture fusing frozen CNN V4 visual features (128-d) and MediaPipe geometric landmarks (64-d).</p>
          <div className="metric-row"><span>Validation Accuracy</span><b>{REPORT.fusionValAcc}%</b></div>
          <div className="metric-row"><span>Macro F1 Score</span><b>{REPORT.fusionMacroF1}%</b></div>
          <div className="metric-row"><span>Total Parameters</span><b>331,610 (26,426 trainable)</b></div>
          <div className="metric-row"><span>Input Modalities</span><b>128×128 Image + 78-d Landmarks</b></div>
          <div className="metric-row"><span>Fallback Guarantee</span><b>Automatic CNN V4 Degradation</b></div>
        </div>

        <div className="model-card">
          <h3>CNN V4 (Visual Baseline) <span className="badge blue">Frozen</span></h3>
          <p className="tip">Deep convolutional network with batch normalization and L2 regularization.</p>
          <div className="metric-row"><span>Independent Test Accuracy</span><b>{REPORT.testAcc}%</b></div>
          <div className="metric-row"><span>Validation Accuracy</span><b>80.14%</b></div>
          <div className="metric-row"><span>Macro F1 Score</span><b>{REPORT.macroF1}% (Test) · 77.68% (Val)</b></div>
          <div className="metric-row"><span>Parameters</span><b>308,218</b></div>
          <div className="metric-row"><span>Input Shape</span><b>128×128×3 RGB</b></div>
          <div className="metric-row"><span>Target Conv Layer</span><b>block3_conv2</b></div>
        </div>
      </div>

      <div className="two">
        <div className="model-card">
          <h3>Geometric Landmark MLP <span className="badge">Geometric</span></h3>
          <p className="tip">Multilayer perceptron operating strictly on scale-invariant 78-d landmark features.</p>
          <div className="metric-row"><span>Validation Accuracy</span><b>{REPORT.landmarkValAcc}% (RF: {REPORT.landmarkRfAcc}%)</b></div>
          <div className="metric-row"><span>Validation Macro F1</span><b>63.77% (RF: 72.44%)</b></div>
          <div className="metric-row"><span>Parameters</span><b>18,458</b></div>
          <div className="metric-row"><span>Input Dimension</span><b>78 Normalized Features</b></div>
          <div className="metric-row"><span>Key Benefit</span><b>Lighting & Background Invariant</b></div>
        </div>

        <div className="model-card">
          <h3>Temporal Dynamic Gesture (BiLSTM/BiGRU) <span className="badge warn">Dynamic Prototype</span></h3>
          <p className="tip">Bidirectional recurrent networks for dynamic moving sign trajectories (J, Z).</p>
          <div className="metric-row"><span>Sequence Window</span><b>30 Frames (~1.0s @ 30fps)</b></div>
          <div className="metric-row"><span>Parameters</span><b>BiLSTM: 118,787 · BiGRU: 89,667</b></div>
          <div className="metric-row"><span>Architectural Status</span><b>Verified Recurrent Infrastructure</b></div>
          <div className="metric-row"><span>Physical Video Dataset</span><b>In Ongoing Collection (RealSign is static)</b></div>
        </div>
      </div>

      {/* Interactive Comparative Tester */}
      <div className="panel" style={{ marginTop: 24 }}>
        <h2>Live Multi-Model Comparison</h2>
        <p className="tip">Upload an image to run CNN V4, Landmark MLP, and Multimodal Fusion concurrently.</p>
        <div className="row wrap">
          <input type="file" accept="image/png,image/jpeg" onChange={handleUploadCompare} />
          {loading && <span>Evaluating all models…</span>}
        </div>
        {err && <p className="err">{err}</p>}

        {compResult && (
          <div className="three" style={{ marginTop: 16 }}>
            <div className="panel" style={{ textAlign: "center" }}>
              <small>CNN V4 Baseline</small>
              <div style={{ font: "800 3rem var(--disp)", color: "var(--blue)" }}>{compResult.cnn_v4.letter}</div>
              <p className="tip">{(compResult.cnn_v4.confidence * 100).toFixed(1)}% Confidence</p>
            </div>
            <div className="panel" style={{ textAlign: "center" }}>
              <small>Geometric Landmark MLP</small>
              <div style={{ font: "800 3rem var(--disp)", color: "var(--accent)" }}>{compResult.landmark_mlp.letter}</div>
              <p className="tip">{(compResult.landmark_mlp.confidence * 100).toFixed(1)}% Confidence</p>
            </div>
            <div className="panel" style={{ textAlign: "center", border: "2px solid var(--ok)" }}>
              <small>Multimodal Fusion Head</small>
              <div style={{ font: "800 3rem var(--disp)", color: "var(--ok)" }}>{compResult.multimodal_fusion.letter}</div>
              <p className="tip">{(compResult.multimodal_fusion.confidence * 100).toFixed(1)}% Confidence</p>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

function Learn({ go, setTarget }) {
  const [q, setQ] = useState("");
  const [sel, setSel] = useState(null);
  const shown = LETTERS.filter((l) => l.includes(q.toUpperCase()));
  const hard = REPORT.hard;

  return (
    <section>
      <h1 className="h2">Learn ISL Alphabet (A–Z)</h1>
      <p className="lead">Study authentic Indian Sign Language fingerspelling postures and practice them in real-time.</p>
      <input
        className="search"
        placeholder="Filter by letter…"
        value={q}
        maxLength={1}
        onChange={(e) => setQ(e.target.value)}
        aria-label="Filter letter"
      />
      <div className="grid">
        {shown.map((l) => (
          <button key={l} className="card" onClick={() => setSel(l)}>
            <Sign l={l} />
            <b>{l}</b>
            {hard[l] && <small>Challenging class</small>}
          </button>
        ))}
        {!shown.length && <p className="tip">No letter matches. Enter a letter A–Z.</p>}
      </div>

      {sel && (
        <div className="modal" role="dialog" aria-modal="true" aria-label={`Letter ${sel}`} onClick={() => setSel(null)}>
          <div onClick={(e) => e.stopPropagation()}>
            <Sign l={sel} big />
            <h2>Letter {sel}</h2>
            {hard[sel] && <p className="warn">Held-out test benchmark difficulty: {hard[sel]}. Focus on clear finger alignment.</p>}
            {(sel === "J" || sel === "Z") && <p className="warn">J and Z naturally involve motion trajectories.</p>}
            <div className="row wrap" style={{ justifyContent: "center", marginTop: 16 }}>
              <button className="btn primary" onClick={() => { setTarget(sel); go("studio"); }}>Practice {sel} in Studio</button>
              <button className="btn" onClick={() => setSel(null)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

function Sign({ l, big }) {
  const [bad, setBad] = useState(false);
  return bad ? (
    <span className={`ph ${big ? "big" : ""}`}>{l}</span>
  ) : (
    <img
      className={big ? "sign big" : "sign"}
      src={`/signs/${l}.jpg`}
      alt={`Sign posture ${l}`}
      onError={() => setBad(true)}
    />
  );
}

function Dashboard({ h, ok }) {
  const { hist, clear } = h;
  const counts = hist.reduce((m, e) => ((m[e.letter] = (m[e.letter] || 0) + 1), m), {});
  const top = Object.entries(counts).sort((a, b) => b[1] - a[1])[0];
  const avg = hist.length ? hist.reduce((s, e) => s + e.conf, 0) / hist.length : 0;
  const bins = Array.from({ length: 5 }, (_, i) => hist.filter((e) => Math.min(4, Math.floor(e.conf * 5)) === i).length);
  const max = Math.max(1, ...bins);

  return (
    <section>
      <h1 className="h2">System Analytics & Dashboard</h1>
      <div className="two">
        <div className="panel">
          <h2>Verified Model Baseline <small>Quarantined Test Set</small></h2>
          <dl className="kv">
            <dt>Test Accuracy</dt><dd>{REPORT.testAcc}%</dd>
            <dt>Macro F1 Score</dt><dd>{REPORT.macroF1}%</dd>
            <dt>Held-Out Samples</dt><dd>{REPORT.correct}</dd>
            <dt>Alphabet Classes</dt><dd>26 (A–Z)</dd>
            <dt>Temperature Scaling (T)</dt><dd>1.28</dd>
            <dt>Backend Status</dt><dd>{ok === null ? "Checking…" : ok ? "Online" : "Offline"}</dd>
          </dl>
        </div>

        <div className="panel">
          <h2>Current Session Diagnostics <small>Client-Side</small></h2>
          {hist.length ? (
            <>
              <dl className="kv">
                <dt>Predictions Logged</dt><dd>{hist.length}</dd>
                <dt>Most Frequent Sign</dt><dd>{top[0]} ({top[1]}×)</dd>
                <dt>Mean Confidence</dt><dd>{(avg * 100).toFixed(1)}%</dd>
              </dl>
              <div className="hist" aria-label="Confidence distribution">
                {bins.map((n, i) => (
                  <div key={i}>
                    <i style={{ height: `${(n / max) * 100}%` }} />
                    <span>{i * 20}–{i * 20 + 20}%</span>
                  </div>
                ))}
              </div>
              <button className="btn" onClick={clear}>Clear History</button>
            </>
          ) : (
            <p className="tip">No predictions recorded yet. Launch the Studio to begin logging data.</p>
          )}
        </div>
      </div>

      {hist.length > 0 && (
        <div className="panel">
          <h2>Recent Inference Log</h2>
          <table>
            <thead>
              <tr><th>Timestamp</th><th>Predicted Letter</th><th>Confidence</th><th>Latency</th></tr>
            </thead>
            <tbody>
              {hist.slice(0, 10).map((e) => (
                <tr key={e.t}>
                  <td>{new Date(e.t).toLocaleTimeString()}</td>
                  <td><b>{e.letter}</b></td>
                  <td>{(e.conf * 100).toFixed(1)}%</td>
                  <td>{Math.round(e.ms ?? 0)} ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function Bars({ rows, color }) {
  return (
    <ul className="bars">
      {rows.map(([k, v]) => (
        <li key={k}>
          <span>{k}</span>
          <i style={{ "--w": `${v}%`, "--c": color?.(k, v) }} />
          <b>{v}%</b>
        </li>
      ))}
    </ul>
  );
}

function Performance() {
  return (
    <section>
      <h1 className="h2">Performance & Empirical Rigor</h1>
      <div className="two">
        <div className="panel">
          <h2>Model Iterations <small>Validation Macro F1</small></h2>
          <Bars rows={REPORT.versions} color={(k) => (k === "V4" ? "var(--blue)" : "var(--mute)")} />
          <p className="tip">CNN V4 with L2 kernel regularization achieved optimal generalization balance.</p>
        </div>
        <div className="panel">
          <h2>Perturbation Robustness <small>Stress-Tested Accuracy</small></h2>
          <Bars rows={REPORT.robust} color={(k, v) => (v < 60 ? "var(--warn)" : "var(--blue)")} />
          <p className="tip">Severe illumination reduction and contrast loss highlight real-world physical camera sensitivities.</p>
        </div>
      </div>
      <div className="panel">
        <h2>Held-Out Test Confusion Matrix</h2>
        <img
          className="cm"
          src="/results/confusion_matrix.png"
          alt="Confusion matrix"
          onError={(e) => {
            e.currentTarget.replaceWith(
              Object.assign(document.createElement("p"), {
                className: "tip",
                textContent: "Confusion matrix rendered from results/final/confusion_matrix.png.",
              })
            );
          }}
        />
      </div>
    </section>
  );
}

function About() {
  return (
    <section className="about">
      <h1 className="h2">About SignAI 2.0</h1>
      <p className="lead">Multimodal Indian Sign Language Alphabet Recognition Research Prototype.</p>
      <div className="two">
        <div className="panel">
          <h2>Multimodal Architecture</h2>
          <p>
            Integrates deep convolutional vision (CNN V4) with MediaPipe Hand Landmarker 21-point 3D kinematic tracking,
            Grad-CAM explainability, and confidence calibration to advance accessibility interfaces.
          </p>
        </div>
        <div className="panel">
          <h2>Engineering Stack</h2>
          <p>
            Frontend: React 19, Vite, HTML5 Canvas. Backend: Python FastAPI, TensorFlow/Keras, MediaPipe Tasks Vision,
            OpenCV, Pillow, Scikit-learn.
          </p>
        </div>
      </div>
      <div className="panel caution">
        <h2>Ethical Principles & Technical Limitations</h2>
        <ul>
          <li><b>Fingerspelling Scope:</b> Recognizes isolated alphabet letters (A–Z). Does not replace professional sign language interpreters.</li>
          <li><b>Dynamic Signs:</b> J and Z involve motion trajectories; temporal sequence infrastructure is provided.</li>
          <li><b>Signer Generalization:</b> Evaluated on the held-out test split of the 25,085 RealSign image dataset.</li>
          <li><b>Optical Requirements:</b> Extreme low light or blurred motion impairs landmark extraction and confidence.</li>
        </ul>
      </div>
    </section>
  );
}
