/* global React */
const { useState: useStateRd, useEffect: useEffectRd } = React;

// Generated from the actual agent registry in runner.py
const AGENT_SEQUENCE = [
  ["loader",                  "Loading catalogue · {n} rows"],
  ["resolver",                "Resolving ISRCs · matched {nm} of {n}"],
  ["rights_check",            "Rights check · {n} / {n} clean"],
  ["spotify_track",           "Pulling Spotify track signals · 90d window"],
  ["spotify_track_historic",  "Reading Spotify historic curves"],
  ["instagram_track",         "Pulling Instagram audio reuse"],
  ["instagram_track_historic","Reading Instagram historic curves"],
  ["instagram_video",         "Reading top 5 IG videos per flagged track"],
  ["tiktok_track",            "Pulling TikTok audio reuse · creator counts"],
  ["tiktok_track_historic",   "Reading TikTok historic curves"],
  ["tiktok_video",            "Reading top 5 TikTok videos per flagged track"],
  ["youtube_track",           "Pulling YouTube long-form views"],
  ["youtube_track_historic",  "Reading YouTube historic curves"],
  ["youtube_video",           "Reading top 5 YouTube videos per flagged track"],
  ["youtube_shorts",          "Reading YouTube Shorts seeding signals"],
  ["period_track",            "Aligning tracks to calendar windows"],
  ["spotify_artist",          "Reading artist profiles · Spotify"],
  ["instagram_artist",        "Reading artist profiles · Instagram"],
  ["tiktok_artist",           "Reading artist profiles · TikTok"],
  ["youtube_artist",          "Reading artist profiles · YouTube"],
  ["track_summarizer",        "Composing per-track reasoning · {n} tracks"],
  ["artist_summarizer",       "Composing per-artist reasoning"],
  ["rank_and_flag",           "Ranking · flagging top tracks"],
];

// Map agent name → index in AGENT_SEQUENCE for step highlighting
const AGENT_TO_STEP = {};
AGENT_SEQUENCE.forEach(([name], idx) => { AGENT_TO_STEP[name] = idx; });

function pad2(n) { return n < 10 ? "0" + n : "" + n; }
function fmtTs(secondsOffset) {
  const total = 6 * 3600 + 42 * 60 + 8 + Math.floor(secondsOffset);
  const h = Math.floor(total / 3600) % 24;
  const m = Math.floor(total / 60) % 60;
  const s = total % 60;
  return `${pad2(h)}:${pad2(m)}:${pad2(s)}`;
}

function Reading({ catalogue, onDone }) {
  const [step, setStep] = useStateRd(0);
  const [pct, setPct] = useStateRd(0);
  const total = AGENT_SEQUENCE.length;
  const n = catalogue ? catalogue.tracks : 0;
  const nm = Math.max(0, n - 4);

  // If catalogue.id is a real backend integer, poll status; otherwise fall back to timer
  const backendId = catalogue && typeof catalogue.id === "number" ? catalogue.id : null;

  useEffectRd(() => {
    if (backendId == null) {
      // Demo fallback: timer-driven progression
      const duration = 5400;
      const tickMs = duration / total;
      if (step >= total) {
        const t = setTimeout(() => onDone && onDone(), 400);
        return () => clearTimeout(t);
      }
      const t = setTimeout(() => setStep(s => s + 1), tickMs);
      return () => clearTimeout(t);
    }
  }, [backendId, step, total, onDone]);

  useEffectRd(() => {
    if (backendId == null) return;

    let active = true;

    async function poll() {
      try {
        const r = await fetch(`/api/catalogues/${backendId}/status`);
        if (!r.ok) throw new Error("HTTP " + r.status);
        const data = await r.json();

        if (!active) return;

        const newPct = data.pct || 0;
        setPct(newPct);

        if (data.agent && AGENT_TO_STEP[data.agent] != null) {
          setStep(AGENT_TO_STEP[data.agent]);
        }

        window.dispatchEvent(new CustomEvent("catalyst:processing-progress", {
          detail: { id: backendId, pct: newPct }
        }));

        if (data.status === "done" || data.status === "error") {
          setStep(total);
          setPct(100);
          setTimeout(() => { if (active) onDone && onDone(); }, 400);
          return;
        }

        if (active) setTimeout(poll, 2000);
      } catch (_) {
        if (active) setTimeout(poll, 3000);
      }
    }

    poll();
    return () => { active = false; };
  }, [backendId]);

  // For demo mode, pct is derived from step; for backend mode, pct comes from poll
  const displayPct = backendId != null ? pct : Math.min(100, Math.round((step / total) * 100));

  const etaSec = backendId != null
    ? null  // backend doesn't expose ETA
    : Math.max(0, Math.round(((total - step) * (5400 / total)) / 1000));
  const etaText = displayPct >= 100 ? "—"
    : etaSec == null ? "In progress"
    : `${Math.floor(etaSec / 60)} min ${pad2(etaSec % 60)} sec`;

  const visibleStart = Math.max(0, step - 9);
  const lines = AGENT_SEQUENCE.slice(visibleStart, Math.min(total, step + 4)).map((row, i) => {
    const idx = visibleStart + i;
    let cls = "pending";
    if (idx < step) cls = "done";
    else if (idx === step) cls = "now";
    const msg = row[1].replaceAll("{n}", n).replaceAll("{nm}", nm);
    return { idx, agent: row[0], msg, cls, ts: idx <= step ? fmtTs(idx * 2.4) : "—:—:—" };
  });

  const tracksRead = Math.round((displayPct / 100) * n);

  return (
    <section className="flex-1 grid fade-in min-h-0" style={{ gridTemplateColumns: "1fr 1fr", background: "#0A0A0A" }}>
      {/* Left — quiet headline */}
      <div className="flex flex-col px-16 py-16" style={{ borderRight: "1px solid #1f1f1f" }}>
        <div className="mono text-[10.5px] uppercase mb-7" style={{ letterSpacing: "0.16em", color: "#5e5e5e" }}>
          {catalogue ? catalogue.name : "Catalogue"} · {n} tracks
        </div>
        <h1 className="text-[44px] font-semibold tighter2 leading-[1.08] mb-4 max-w-[14ch]" style={{ textWrap: "balance" }}>
          Reading against <span style={{ color: "#00E5FF" }}>the four platforms.</span>
        </h1>
        <p className="text-[15px] leading-[1.6] tightish max-w-[44ch]" style={{ color: "#8a8a8a" }}>
          Catalyst is running 14 agents per track against Spotify, Instagram, TikTok and YouTube, then summarising each one. No action is required while this runs.
        </p>

        <div className="mt-auto">
          <div className="flex justify-between mono text-[11px] mb-3" style={{ letterSpacing: "0.04em", color: "#8a8a8a" }}>
            <span>{tracksRead} of {n} tracks read</span>
            <span style={{ color: "#00E5FF" }}>{displayPct}%</span>
          </div>
          <div style={{ height: 2, background: "#1f1f1f", position: "relative" }}>
            <div
              style={{
                position: "absolute", left: 0, top: -1, height: 4,
                width: displayPct + "%",
                background: "#00E5FF",
                boxShadow: "0 0 12px rgba(0,229,255,0.5)",
                transition: "width 0.4s ease"
              }}
            ></div>
          </div>
          <div className="flex justify-between mono text-[10.5px] uppercase mt-4" style={{ letterSpacing: "0.1em", color: "#5e5e5e" }}>
            <span>ETA · {etaText}</span>
            <span>traceable on completion</span>
          </div>
        </div>
      </div>

      {/* Right — live trace */}
      <div className="flex flex-col px-16 py-16" style={{ background: "#0d0d0d" }}>
        <div className="flex justify-between items-center mb-5">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full pulse-dot" style={{ background: "#00E5FF" }}></span>
            <span className="mono text-[10.5px] uppercase font-medium" style={{ letterSpacing: "0.16em", color: "#f4f4f4" }}>Live trace</span>
          </div>
          <span className="mono text-[10.5px] uppercase" style={{ letterSpacing: "0.12em", color: "#5e5e5e" }}>14 agents · per track</span>
        </div>

        <div className="mono text-[11.5px]" style={{ letterSpacing: "0.01em", lineHeight: 1.85 }}>
          {lines.map(l => (
            <div className={"log-line " + l.cls} key={l.idx}>
              <span className="ts">{l.ts}</span>
              <span className="agent">{l.agent}</span>
              <span className={"msg" + (l.cls === "now" ? " blink-caret" : "")}>{l.msg}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

window.Reading = Reading;
