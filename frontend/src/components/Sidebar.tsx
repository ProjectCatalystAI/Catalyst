import { Wordmark } from '../icons';
import type { Catalogue } from '../types';

interface SidebarProps {
  catalogues: Catalogue[];
  activeId: number | string | null;
  processingId: number | string | null;
  processingPct: number;
  onSelect: (id: number | string) => void;
  onAdd: () => void;
}

export default function Sidebar({ catalogues, activeId, onSelect, onAdd, processingId, processingPct }: SidebarProps) {
  const hasCatalogues = catalogues.length > 0;
  const totalTracks = catalogues.reduce((sum, c) => sum + (c.tracks || 0), 0);
  const flaggedCount = hasCatalogues ? 14 : 0; // demo

  return (
    <aside className="w-[280px] shrink-0 border-r border-line py-7 pl-7 pr-5 flex flex-col gap-6 bg-bg" style={{ borderColor: "#1f1f1f", background: "#0A0A0A" }}>
      {/* Brand — wordmark from Catalyst Cover */}
      <div className="flex items-center">
        <Wordmark height={26} />
      </div>

      {/* Add button */}
      <button
        className="add-btn flex items-center justify-between gap-2 px-3.5 py-3 rounded-md border text-left"
        style={{ borderColor: "#2a2a2a", background: "#0d0d0d", color: "#f4f4f4" }}
        onClick={onAdd}
      >
        <span className="flex items-center gap-2.5 text-[13.5px] font-medium tightish">
          <span className="add-glyph mono text-[16px]" style={{ color: "#8a8a8a", lineHeight: 1, marginTop: -2 }}>+</span>
          Add catalogue
        </span>
        <span className="mono text-[10px] px-1.5 py-0.5 rounded" style={{ background: "#161616", color: "#5e5e5e", border: "1px solid #2a2a2a", letterSpacing: "0.06em" }}>N</span>
      </button>

      {/* Portfolio summary — only when populated */}
      {hasCatalogues && (
        <div className="-mb-1">
          <div className="text-[10.5px] uppercase mb-2" style={{ letterSpacing: "0.16em", color: "#5e5e5e" }}>Portfolio</div>
          <div className="text-[26px] font-semibold tighter2 leading-none">{totalTracks.toLocaleString()} tracks</div>
          <div className="text-[12.5px] mt-1.5" style={{ color: "#8a8a8a" }}>across {catalogues.length} catalogue{catalogues.length === 1 ? "" : "s"}</div>
        </div>
      )}

      {/* Catalogue list */}
      <div className="flex flex-col gap-1">
        <div className="text-[10.5px] uppercase mb-2 pl-2 flex justify-between items-center" style={{ letterSpacing: "0.16em", color: "#5e5e5e" }}>
          <span>Your catalogues</span>
          {hasCatalogues && <span className="mono" style={{ letterSpacing: "0.04em" }}>{catalogues.length}</span>}
        </div>

        {!hasCatalogues ? (
          <div className="px-3 py-3 text-[12px] leading-relaxed mono" style={{ color: "#3a3a3a", letterSpacing: "0.02em" }}>
            None yet.<br />
            <span style={{ color: "#2e2e2e" }}>Drop a CSV to begin.</span>
          </div>
        ) : (
          <div className="flex flex-col gap-0.5">
            {catalogues.map(c => {
              const isActive = c.id === activeId;
              const isProc = c.id === processingId;
              return (
                <button
                  key={c.id}
                  className={"cat-item relative flex items-center justify-between px-3 py-2.5 rounded-md border text-left " + (isActive ? "active" : "") + (isProc ? " processing" : "")}
                  style={{
                    borderColor: isActive ? "#2a2a2a" : "transparent",
                    background: isActive ? "#111" : "transparent",
                    cursor: isProc ? "default" : "pointer"
                  }}
                  onClick={() => !isProc && onSelect(c.id)}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <span
                      className={isProc ? "pulse-dot" : ""}
                      style={{
                        width: 6, height: 6, borderRadius: "50%",
                        background: isProc ? "#00E5FF" : (isActive ? "#00E5FF" : "#2a2a2a"),
                        flexShrink: 0
                      }}
                    ></span>
                    <span className="text-[13.5px] font-medium tightish truncate" style={{ color: isActive ? "#f4f4f4" : "#8a8a8a", maxWidth: 165 }}>{c.name}</span>
                  </div>
                  <span className="mono text-[11px]" style={{ color: isProc ? "#00E5FF" : "#5e5e5e", letterSpacing: "0.02em" }}>
                    {isProc ? `${Math.round(processingPct || 0)}%` : (c.tracks ? c.tracks.toLocaleString() : "—")}
                  </span>
                  {isProc && <span className="proc-fill" style={{ width: `calc(${processingPct || 0}% - 0px)` }}></span>}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer — week summary, only when populated */}
      {hasCatalogues && (
        <div className="mt-auto pt-6 border-t" style={{ borderColor: "#1f1f1f" }}>
          <div className="text-[10.5px] uppercase mb-3" style={{ letterSpacing: "0.16em", color: "#5e5e5e" }}>This week</div>
          <div className="flex items-baseline gap-2">
            <span className="text-[22px] font-semibold mono">{flaggedCount}</span>
            <span className="text-[12.5px]" style={{ color: "#8a8a8a" }}>tracks flagged for attention</span>
          </div>
          <div className="flex items-baseline gap-2 mt-1.5">
            <span className="text-[22px] font-semibold mono" style={{ color: "#00E5FF" }}>3</span>
            <span className="text-[12.5px]" style={{ color: "#8a8a8a" }}>hot cultural moments</span>
          </div>
        </div>
      )}
    </aside>
  );
}
