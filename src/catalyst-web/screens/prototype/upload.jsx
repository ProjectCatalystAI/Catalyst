/* global React */
const { useState: useStateUp, useRef: useRefUp } = React;

function Upload({ onCancel, onIngest }) {
  const [over, setOver] = useStateUp(false);
  const inputRef = useRefUp(null);

  function handleFiles(files) {
    if (!files || files.length === 0) return;
    const f = files[0];
    const raw = f.name || "Untitled catalogue.csv";
    const name = raw.replace(/\.csv$/i, "").trim() || "Untitled catalogue";
    onIngest({ name, filename: raw, size: f.size, file: f });
  }

  return (
    <section className="flex-1 fade-in flex items-center justify-center px-10 py-8" style={{ background: "#0A0A0A" }}>
      <div className="w-full max-w-[720px]">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-[12px] mb-5" style={{ color: "#8a8a8a" }}>
          <button className="hover:text-fg" onClick={onCancel} style={{ color: "#8a8a8a" }}>Catalogues</button>
          <span style={{ color: "#3a3a3a" }}>/</span>
          <span style={{ color: "#f4f4f4" }}>Add</span>
        </div>

        {/* Header */}
        <div className="mb-7">
          <div className="text-[10.5px] uppercase mb-2.5" style={{ letterSpacing: "0.16em", color: "#5e5e5e" }}>New catalogue</div>
          <h1 className="text-[40px] font-semibold tighter2 leading-[1.02]">Drop a catalogue.</h1>
          <p className="text-[14.5px] leading-[1.55] tightish mt-3 max-w-[58ch]" style={{ color: "#8a8a8a" }}>
            Catalyst reads the CSV row-by-row, resolves each track against Spotify, then runs the full agent pipeline. The filename becomes the catalogue name.
          </p>
        </div>

        {/* Dropzone */}
        <div
          className={"dropzone rounded-lg px-12 py-16 text-center cursor-pointer relative" + (over ? " over" : "")}
          style={{
            border: "1px dashed " + (over ? "#00E5FF" : "#2a2a2a"),
            background: over ? "rgba(0,229,255,0.04)" : "#0d0d0d"
          }}
          onDragEnter={e => { e.preventDefault(); setOver(true); }}
          onDragOver={e => { e.preventDefault(); setOver(true); }}
          onDragLeave={e => { e.preventDefault(); setOver(false); }}
          onDrop={e => {
            e.preventDefault();
            setOver(false);
            handleFiles(e.dataTransfer.files);
          }}
          onClick={() => inputRef.current && inputRef.current.click()}
        >
          <div
            className="mx-auto mb-5 grid place-items-center"
            style={{
              width: 40, height: 40,
              border: "1px solid " + (over ? "#00E5FF" : "#3a3a3a"),
              borderRadius: 4,
              color: over ? "#00E5FF" : "#8a8a8a",
              position: "relative"
            }}
          >
            <span style={{ position: "absolute", inset: 8, border: "1px solid currentColor", borderRadius: 2 }}></span>
            <span className="mono" style={{ fontSize: 16, fontWeight: 500, position: "relative", zIndex: 1, background: over ? "rgba(0,229,255,0.06)" : "#0d0d0d", padding: "0 3px" }}>+</span>
          </div>
          <div className="text-[22px] font-semibold tightish mb-1.5">
            {over ? <span style={{ color: "#00E5FF" }}>Release to read.</span> : <span>Drag a <span className="mono" style={{ color: "#00E5FF" }}>.csv</span> here.</span>}
          </div>
          <div className="mono text-[11px] uppercase" style={{ letterSpacing: "0.1em", color: "#8a8a8a" }}>
            artist · title · isrc · optional notes
          </div>
          <div className="mt-6 inline-flex items-center gap-3">
            <button
              type="button"
              className="h-10 px-4 rounded-md font-medium text-[13px] tightish"
              style={{ background: "#161616", border: "1px solid #2a2a2a", color: "#f4f4f4" }}
              onClick={e => { e.stopPropagation(); inputRef.current && inputRef.current.click(); }}
            >
              Choose file
            </button>
            <span className="mono text-[10px] uppercase" style={{ letterSpacing: "0.12em", color: "#5e5e5e" }}>or drop</span>
          </div>
          <input
            ref={inputRef}
            type="file"
            accept=".csv,text/csv"
            style={{ display: "none" }}
            onChange={e => handleFiles(e.target.files)}
          />
        </div>

        {/* Schema */}
        <div className="mt-6 grid gap-5 pt-5" style={{ gridTemplateColumns: "110px 1fr", borderTop: "1px solid #1f1f1f" }}>
          <div className="mono text-[10.5px] uppercase pt-1" style={{ letterSpacing: "0.12em", color: "#5e5e5e" }}>Schema</div>
          <div className="text-[13px] leading-[1.6] tightish" style={{ color: "#8a8a8a" }}>
            Header row required. Recognised columns: <code className="mono px-1.5 py-px rounded" style={{ background: "#161616", border: "1px solid #2a2a2a", color: "#f4f4f4", fontSize: 12 }}>artist</code> <code className="mono px-1.5 py-px rounded" style={{ background: "#161616", border: "1px solid #2a2a2a", color: "#f4f4f4", fontSize: 12 }}>title</code> <code className="mono px-1.5 py-px rounded" style={{ background: "#161616", border: "1px solid #2a2a2a", color: "#f4f4f4", fontSize: 12 }}>isrc</code> <code className="mono px-1.5 py-px rounded" style={{ background: "#161616", border: "1px solid #2a2a2a", color: "#f4f4f4", fontSize: 12 }}>year</code> <code className="mono px-1.5 py-px rounded" style={{ background: "#161616", border: "1px solid #2a2a2a", color: "#f4f4f4", fontSize: 12 }}>catalogue_id</code>. Extra columns are kept on the track record.
          </div>
          <div className="mono text-[10.5px] uppercase pt-1" style={{ letterSpacing: "0.12em", color: "#5e5e5e" }}>Limits</div>
          <div className="text-[13px] leading-[1.6] tightish" style={{ color: "#8a8a8a" }}>
            Up to 25,000 rows per file. Larger lists must be split — Catalyst will dedupe on ISRC across catalogues in the same workspace.
          </div>
        </div>
      </div>
    </section>
  );
}

window.Upload = Upload;
