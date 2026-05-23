import { useEffect, useState } from 'react';

import { fetchResults } from '../api/catalogues';
import { FLOW_DATA } from '../data/flowData';
import { PlatformIcon, PlatformIndicator } from '../icons';
import type { Catalogue, Lens, LensView, PlatformKey, Signals, Track } from '../types';

const PLATFORM_ORDER: PlatformKey[] = ['spotify', 'instagram', 'tiktok', 'youtube'];

const EMPTY_SIGNALS: Signals = { spotify: 0, instagram: 0, tiktok: 0, youtube: 0 };

type DetailEntry = { seasonal: LensView; social: LensView };

interface ResultRowProps {
  track: Track;
  lens: Lens;
  details: Record<number, DetailEntry | undefined>;
  expanded: boolean;
  onClick: () => void;
}

function ResultRow({ track, lens, details, expanded, onClick }: ResultRowProps) {
  const det = details[track.id];
  const view = det ? det[lens] : null;
  const isHot = view ? view.hot : false;
  const signals: Signals = view ? view.signals : EMPTY_SIGNALS;
  const synth = view ? view.synth : (track.lit ? "Flagged — reasoning not yet generated for this lens." : "Outside this lens.");
  const dim = !track.lit && !view;

  const rowStyle = {
    gridTemplateColumns: "16px 1fr 360px 200px",
    background: isHot ? "#0d0d0d" : "#0c0c0c",
    borderLeft: isHot ? "1px solid #0e3e44" : "1px solid transparent",
    opacity: dim ? 0.5 : 1,
    cursor: "pointer"
  };

  if (!expanded) {
    return (
      <div className="row-hover grid gap-6 items-center px-5 py-4" style={rowStyle} onClick={onClick}>
        <span>
          {isHot && <span className="w-2 h-2 rounded-full pulse-dot block" style={{ background: "#00E5FF" }} title="Hot cultural moment"></span>}
        </span>
        <div>
          <div className="text-[15.5px] font-semibold tightish leading-snug" style={{ color: "#f4f4f4" }}>
            {track.title}
          </div>
          <div className="text-[12.5px] mt-0.5" style={{ color: "#8a8a8a" }}>
            {track.artist} · {track.year || "—"}
          </div>
        </div>
        <div className="text-[13px] leading-snug" style={{ color: isHot ? "#7fe7f5" : "#8a8a8a" }}>
          {synth}
        </div>
        <div className="flex items-center gap-2 justify-end">
          {PLATFORM_ORDER.map(k => {
            const v = signals[k] || 0;
            return (
              <PlatformIndicator key={k} kind={k} on={v > 0} pulse={v === 2} />
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <div style={{ ...rowStyle, cursor: "default", display: "block", padding: 0, opacity: 1 }}>
      <div
        className="row-hover grid gap-6 items-center px-5 py-4"
        style={{ gridTemplateColumns: "16px 1fr 360px 200px", borderLeft: isHot ? "1px solid #0e3e44" : "1px solid transparent", cursor: "pointer" }}
        onClick={onClick}
      >
        <span>
          {isHot && <span className="w-2 h-2 rounded-full pulse-dot block" style={{ background: "#00E5FF" }}></span>}
        </span>
        <div>
          <div className="text-[15.5px] font-semibold tightish leading-snug" style={{ color: "#f4f4f4" }}>{track.title}</div>
          <div className="text-[12.5px] mt-0.5" style={{ color: "#8a8a8a" }}>{track.artist} · {track.year || "—"}</div>
        </div>
        <div className="text-[13px] leading-snug" style={{ color: isHot ? "#7fe7f5" : "#8a8a8a" }}>{synth}</div>
        <div className="flex items-center gap-2 justify-end">
          {PLATFORM_ORDER.map(k => {
            const v = signals[k] || 0;
            return <PlatformIndicator key={k} kind={k} on={v > 0} pulse={v === 2} />;
          })}
        </div>
      </div>

      {/* Expansion body */}
      <div className="grid gap-8 px-5 pb-6 pt-1" style={{ gridTemplateColumns: "1fr 280px", background: "#0c0c0c" }}>
        <div className="pl-[22px] flex gap-5">
          <div className="w-[2px] rounded-full" style={{ background: "#00E5FF", flexShrink: 0 }}></div>
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2.5">
              <span className="mono text-[10px] uppercase" style={{ letterSpacing: "0.16em", color: "rgba(0,229,255,0.7)" }}>
                {lens === "seasonal" ? "Period · Summarizer" : "Social · Summarizer"}
              </span>
            </div>
            <p className="text-[15px] leading-[1.65] tightish max-w-[60ch]" style={{ color: "#f4f4f4", textWrap: "pretty" }}>
              {view ? view.reason : "No reasoning generated for this lens."}
            </p>
            <div className="flex flex-wrap gap-1.5 mt-4">
              {Object.entries(view ? view.stats : {}).slice(0, 4).map(([k, v]) => (
                <span key={k} className="tag" style={{ color: "#8a8a8a" }}>
                  {k} · <span style={{ color: "#f4f4f4", textTransform: "none", letterSpacing: 0, marginLeft: 4 }}>{v}</span>
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Right column — signal panel */}
        <div className="rounded-md p-4" style={{ background: "#0A0A0A", border: "1px solid #1f1f1f" }}>
          <div className="mono text-[10px] uppercase mb-3" style={{ letterSpacing: "0.16em", color: "#5e5e5e" }}>Signal map</div>
          <div className="flex flex-col gap-2">
            {([
              ["spotify", "Spotify"],
              ["instagram", "Instagram"],
              ["tiktok", "TikTok"],
              ["youtube", "YouTube"],
            ] as Array<[PlatformKey, string]>).map(([k, label]) => {
              const v = signals[k] || 0;
              const dotColor = v === 2 ? "#00E5FF" : (v === 1 ? "#f4f4f4" : "#2a2a2a");
              const state = v === 2 ? "hot" : v === 1 ? "live" : "—";
              return (
                <div key={k} className="flex items-center justify-between text-[12px]">
                  <span className="flex items-center gap-2.5" style={{ color: "#8a8a8a" }}>
                    <span style={{ color: v > 0 ? "#f4f4f4" : "#3a3a3a", display: "inline-flex" }}>
                      <PlatformIcon kind={k} size={14} />
                    </span>
                    <span>{label}</span>
                  </span>
                  <span className="flex items-center gap-2 mono text-[10.5px]" style={{ letterSpacing: "0.1em", textTransform: "uppercase", color: v > 0 ? "#f4f4f4" : "#3a3a3a" }}>
                    <span className={v === 2 ? "pulse-dot" : ""} style={{ width: 6, height: 6, borderRadius: "50%", background: dotColor }}></span>
                    {state}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

interface ResultsProps {
  catalogue: Catalogue;
}

export default function Results({ catalogue }: ResultsProps) {
  const [lens, setLens] = useState<Lens>("seasonal");
  const [openId, setOpenId] = useState<number | null>(null);
  const [tracks, setTracks] = useState<Track[]>([]);
  const [details, setDetails] = useState<Record<number, DetailEntry | undefined>>({});
  const [loading, setLoading] = useState(true);

  const backendId = catalogue && typeof catalogue.id === "number" ? catalogue.id : null;

  useEffect(() => {
    if (backendId == null) {
      // Fall back to demo data — only seasonal.tracks is used; details stays empty
      // so the fallback synth message shows.
      const demoTracks = FLOW_DATA.seasonal.tracks as unknown as Track[];
      setTracks(demoTracks);
      setLoading(false);
      return;
    }

    setLoading(true);
    fetchResults(backendId)
      .then(data => {
        const apiTracks = data.tracks || [];
        setTracks(apiTracks);
        const map: Record<number, DetailEntry> = {};
        apiTracks.forEach(t => {
          map[t.id] = { seasonal: t.seasonal, social: t.social };
        });
        setDetails(map);
        if (apiTracks.length > 0) setOpenId(apiTracks[0].id);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [backendId]);

  const flaggedCount = tracks.filter(t => {
    const d = details[t.id];
    return d && d[lens] && d[lens].hot;
  }).length;

  if (loading) {
    return (
      <section className="flex-1 flex items-center justify-center fade-in" style={{ background: "#0A0A0A" }}>
        <div className="mono text-[11px] uppercase" style={{ letterSpacing: "0.16em", color: "#5e5e5e" }}>Loading results…</div>
      </section>
    );
  }

  return (
    <section className="flex-1 flex flex-col fade-in min-h-0 overflow-hidden" style={{ background: "#0A0A0A" }}>
      {/* Header */}
      <div className="px-10 pt-7 pb-6 flex items-end justify-between gap-8" style={{ borderBottom: "1px solid #1f1f1f" }}>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-3 text-[12px]" style={{ color: "#8a8a8a" }}>
            <span style={{ color: "#5e5e5e" }}>Catalogues</span>
            <span style={{ color: "#3a3a3a" }}>/</span>
            <span style={{ color: "#f4f4f4" }}>{catalogue.name}</span>
          </div>
          <div className="mono text-[10.5px] uppercase mb-2" style={{ letterSpacing: "0.16em", color: "#5e5e5e" }}>
            Activation ranking · next 90 days
          </div>
          <h1 className="text-[34px] font-semibold tighter2 leading-none">What needs you this week</h1>
          <div className="text-[13px] mt-3" style={{ color: "#8a8a8a" }}>
            {tracks.length} tracks read · <span style={{ color: "#f4f4f4" }}>{flaggedCount} flagged</span> · ordered by activation potential · <span style={{ color: "#00E5FF" }}>cyan headline</span> = what changed this week
          </div>
        </div>

        {/* Lens segmented toggle */}
        <div className="flex p-1 rounded-md text-[12.5px]" style={{ border: "1px solid #1f1f1f", background: "#111" }}>
          <button
            className={"px-3.5 py-1.5 rounded-[5px] font-medium tightish"}
            style={{
              background: lens === "seasonal" ? "#161616" : "transparent",
              color: lens === "seasonal" ? "#f4f4f4" : "#8a8a8a"
            }}
            onClick={() => setLens("seasonal")}
          >
            Seasonal moment
          </button>
          <button
            className={"px-3.5 py-1.5 rounded-[5px] font-medium tightish"}
            style={{
              background: lens === "social" ? "#161616" : "transparent",
              color: lens === "social" ? "#f4f4f4" : "#8a8a8a"
            }}
            onClick={() => setLens("social")}
          >
            Social trend
          </button>
        </div>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto px-10 py-6">
        <div className="rounded-lg overflow-hidden flex flex-col gap-px" style={{ background: "#1f1f1f", border: "1px solid #1f1f1f" }}>
          {/* Header row */}
          <div className="grid gap-6 px-5 py-2.5 mono text-[10px] uppercase" style={{ gridTemplateColumns: "16px 1fr 360px 200px", background: "#0A0A0A", letterSpacing: "0.16em", color: "#5e5e5e" }}>
            <span></span>
            <span>Track · Artist</span>
            <span>This week's synthesis</span>
            <span className="text-right pr-1">Signal across platforms</span>
          </div>
          {tracks.map(t => (
            <ResultRow
              key={t.id}
              track={t}
              lens={lens}
              details={details}
              expanded={openId === t.id}
              onClick={() => setOpenId(openId === t.id ? null : t.id)}
            />
          ))}
        </div>
      </div>

      {/* Bottom analyzer strip */}
      <AnalyzerStrip catalogue={catalogue} />
    </section>
  );
}

interface AnalyzerStripProps {
  catalogue: Catalogue;
}

function AnalyzerStrip({ catalogue }: AnalyzerStripProps) {
  const n = catalogue ? catalogue.tracks : 0;
  const cells: Array<{ kind: PlatformKey; title: string; sub: string; active: boolean }> = [
    { kind: "spotify",   title: "Spotify Analyzer",   sub: `Scanning ${n.toLocaleString()} tracks`, active: false },
    { kind: "instagram", title: "Instagram Analyzer", sub: "14 top videos analysed today", active: false },
    { kind: "tiktok",    title: "TikTok Analyzer",    sub: "Monitoring 12 trending sounds", active: true },
    { kind: "youtube",   title: "YouTube Analyzer",   sub: "6 shorts analysed today", active: false },
  ];
  return (
    <div className="grid gap-px" style={{ gridTemplateColumns: "1fr 1fr 1fr 1fr", background: "#1f1f1f", borderTop: "1px solid #1f1f1f" }}>
      {cells.map(c => (
        <div key={c.kind} className="flex items-center gap-3.5 px-6" style={{ background: "#0A0A0A", height: 70 }}>
          <span
            className="relative grid place-items-center"
            style={{ width: 32, height: 32, borderRadius: 6, background: "#111", border: "1px solid " + (c.active ? "rgba(0,229,255,0.4)" : "#2a2a2a") }}
          >
            <PlatformIcon kind={c.kind} size={14} />
            <span className="absolute pulse-dot" style={{ top: -2, right: -2, width: 6, height: 6, borderRadius: "50%", background: "#00E5FF" }}></span>
          </span>
          <div className="min-w-0">
            <div className="text-[12.5px] font-semibold tightish leading-tight">
              {c.title}
              {c.active && <span className="ml-1.5" style={{ color: "#00E5FF" }}>·active</span>}
            </div>
            <div className="mono text-[11px] leading-tight mt-0.5 truncate" style={{ color: c.active ? "#00E5FF" : "#8a8a8a", letterSpacing: "0.02em" }}>{c.sub}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
