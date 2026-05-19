/* global React, PlatformIndicator */

function EmptyState({ onAdd }) {
  // Ghost rows mimic the populated activation-ranking list, faded back so the
  // user sees what the screen will contain once a catalogue is added.
  const ghostRows = [
    { hot: true,  title: "—————————", sub: "————— · ————" },
    { hot: false, title: "——————————————", sub: "————— · ————" },
    { hot: true,  title: "————————", sub: "————— · ————" },
    { hot: false, title: "—————————————", sub: "————— · ————" },
    { hot: false, title: "———————", sub: "————— · ————" },
    { hot: true,  title: "—————————", sub: "————— · ————" },
    { hot: false, title: "———————————", sub: "————— · ————" },
  ];

  return (
    <section className="flex-1 relative overflow-hidden fade-in" style={{ background: "#0A0A0A" }}>
      {/* Ghost preview behind */}
      <div className="absolute inset-0 px-10 py-8 ghost-row" aria-hidden="true">
        <div className="text-[10.5px] uppercase mb-2" style={{ letterSpacing: "0.16em", color: "#3a3a3a" }}>Activation ranking · next 90 days</div>
        <div className="text-[34px] font-semibold tighter2 leading-none mb-7" style={{ color: "#2a2a2a" }}>What needs you this week</div>

        <div className="flex flex-col gap-px rounded-lg overflow-hidden" style={{ background: "#1f1f1f", border: "1px solid #1f1f1f" }}>
          <div className="grid gap-6 px-5 py-2.5 text-[10px] uppercase" style={{ gridTemplateColumns: "16px 1fr 360px 200px", letterSpacing: "0.16em", color: "#2e2e2e", background: "#0A0A0A" }}>
            <span></span>
            <span>Track · Artist</span>
            <span>This week's synthesis</span>
            <span className="text-right pr-1">Signal across platforms</span>
          </div>
          {ghostRows.map((r, i) => (
            <div
              key={i}
              className="grid gap-6 items-center px-5 py-4"
              style={{ gridTemplateColumns: "16px 1fr 360px 200px", background: "#0d0d0d", borderLeft: r.hot ? "1px solid #1f1f1f" : "1px solid transparent" }}
            >
              <span style={{ width: 8, height: 8, borderRadius: "50%", background: r.hot ? "#0e3e44" : "transparent" }}></span>
              <div>
                <div className="text-[15.5px] font-semibold tightish" style={{ color: "#2a2a2a" }}>{r.title}</div>
                <div className="text-[12.5px] mt-1" style={{ color: "#1f1f1f" }}>{r.sub}</div>
              </div>
              <div className="text-[13px]" style={{ color: "#1f1f1f" }}>————————————————————————</div>
              <div className="flex items-center gap-2 justify-end" style={{ color: "#2a2a2a" }}>
                <span style={{ width: 14, height: 14, borderRadius: 3, background: "#161616" }}></span>
                <span style={{ width: 14, height: 14, borderRadius: 3, background: "#161616" }}></span>
                <span style={{ width: 14, height: 14, borderRadius: 3, background: "#161616" }}></span>
                <span style={{ width: 14, height: 14, borderRadius: 3, background: "#161616" }}></span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Veil over the ghost so the card on top reads clearly */}
      <div className="absolute inset-0 ghost-veil"></div>

      {/* Centered empty card */}
      <div className="absolute inset-0 grid place-items-center px-10 py-8">
        <div className="relative max-w-[560px] w-full">
          {/* Cyan arrow back to the sidebar + button */}
          <svg className="absolute pointer-events-none" style={{ left: -200, top: 86, width: 210, height: 90 }} viewBox="0 0 210 90" fill="none" aria-hidden="true">
            <path d="M 208 64 Q 110 64 70 40 Q 38 22 6 16" stroke="#00E5FF" strokeOpacity="0.6" strokeWidth="1" strokeDasharray="3 4" fill="none" />
            <path d="M 14 10 L 4 16 L 14 22" stroke="#00E5FF" strokeOpacity="0.8" strokeWidth="1" fill="none" strokeLinecap="round" strokeLinejoin="round" />
          </svg>

          <div className="rounded-lg border p-9" style={{ borderColor: "#1f1f1f", background: "rgba(17,17,17,0.85)", backdropFilter: "blur(6px)" }}>
            <div className="flex items-center gap-2 mb-5">
              <span className="w-1.5 h-1.5 rounded-full pulse-dot" style={{ background: "#00E5FF" }}></span>
              <span className="mono text-[10.5px] uppercase" style={{ letterSpacing: "0.16em", color: "#00E5FF" }}>Catalyst · studio</span>
            </div>
            <h1 className="text-[44px] font-semibold tighter2 leading-[1.02] mb-3">No catalogue yet.</h1>
            <p className="text-[15px] leading-[1.6] tightish mb-7" style={{ color: "#8a8a8a", textWrap: "pretty" }}>
              Catalyst reads a catalogue against Spotify, Instagram, TikTok and YouTube and surfaces the tracks worth your attention this week. Drop a CSV to the left to start.
            </p>

            <ol className="flex flex-col gap-px mb-7 rounded-md overflow-hidden" style={{ background: "#1f1f1f", border: "1px solid #1f1f1f" }}>
              {[
                ["01", <span><b className="text-fg font-medium">Drop a CSV</b>: artist and title are all you need. The filename becomes the catalogue name.</span>],
                ["02", <span>Catalyst runs <b className="text-fg font-medium">14 agents per track</b> across the four platforms, then summarises.</span>],
                ["03", <span>You see the tracks worth playing this week, with the reasoning behind each one.</span>],
              ].map(([n, t]) => (
                <li key={n} className="grid gap-4 px-4 py-3 items-baseline" style={{ gridTemplateColumns: "36px 1fr", background: "#111" }}>
                  <span className="mono text-[10.5px] uppercase" style={{ letterSpacing: "0.12em", color: "#5e5e5e" }}>{n}</span>
                  <span className="text-[13px] leading-[1.5] tightish" style={{ color: "#8a8a8a" }}>{t}</span>
                </li>
              ))}
            </ol>

            <div className="flex items-center gap-4">
              <button
                className="flex items-center gap-2.5 px-4 h-10 rounded-md font-medium text-[13px] tightish cyan-glow"
                style={{ background: "#00E5FF", color: "#0A0A0A", border: "1px solid #00E5FF" }}
                onClick={onAdd}
              >
                Add a catalogue
                <span className="mono text-[10px] px-1.5 py-0.5 rounded" style={{ background: "rgba(10,10,10,0.18)", border: "1px solid rgba(10,10,10,0.2)", letterSpacing: "0.04em", color: "#0A0A0A" }}>N</span>
              </button>
              <span className="mono text-[10.5px] uppercase" style={{ letterSpacing: "0.1em", color: "#5e5e5e" }}>csv · ≤ 25,000 rows</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

window.EmptyState = EmptyState;
