/* global React, ReactDOM, PSidebar, EmptyState, Upload, Reading, Results */
const { useState: useStateApp, useEffect: useEffectApp, useRef: useRefApp } = React;

function App() {
  const [view, setView] = useStateApp("empty");
  const [catalogues, setCatalogues] = useStateApp([]);
  const [activeId, setActiveId] = useStateApp(null);
  const [processingId, setProcessingId] = useStateApp(null);
  const [processingPct, setProcessingPct] = useStateApp(0);
  const idRef = useRefApp(1);

  // Listen for progress events from <Reading />
  useEffectApp(() => {
    function onProgress(e) {
      if (!e.detail) return;
      if (e.detail.id === processingId) setProcessingPct(e.detail.pct);
    }
    window.addEventListener("catalyst:processing-progress", onProgress);
    return () => window.removeEventListener("catalyst:processing-progress", onProgress);
  }, [processingId]);

  // Keyboard shortcuts
  useEffectApp(() => {
    function onKey(e) {
      if (e.target && (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA")) return;
      if (e.key === "n" || e.key === "N") {
        if (view !== "upload" && view !== "reading") setView("upload");
      } else if (e.key === "Escape") {
        if (view === "upload") setView(activeId ? "results" : "empty");
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [view, activeId]);

  function handleAdd() { setView("upload"); }
  function handleCancelUpload() { setView(activeId ? "results" : "empty"); }

  async function handleIngest({ name, filename, size, file }) {
    // Optimistic local entry while we wait for the backend
    const localId = "c-" + (idRef.current++);
    const estTracks = Math.max(24, Math.min(1000, Math.round((size || 12000) / 100)));
    const pending = { id: localId, name, filename, tracks: estTracks, addedAt: Date.now(), lensRun: null };
    setCatalogues(prev => [pending, ...prev]);
    setActiveId(localId);
    setProcessingId(localId);
    setProcessingPct(0);
    setView("reading");

    if (!file) return;
    try {
      const form = new FormData();
      form.append("file", file);
      form.append("name", name);
      const resp = await fetch("/api/catalogues", { method: "POST", body: form });
      if (!resp.ok) throw new Error("Upload failed: " + resp.status);
      const data = await resp.json();
      // Replace the temporary local catalogue with the backend-assigned ID
      setCatalogues(prev => prev.map(c =>
        c.id === localId
          ? { ...c, id: data.id, tracks: data.track_count || estTracks }
          : c
      ));
      setActiveId(data.id);
      setProcessingId(data.id);
    } catch (err) {
      console.error("Catalogue upload failed:", err);
      // Leave the timer-driven demo mode intact — reading.jsx will fall back
    }
  }

  function handleReadingDone() {
    setCatalogues(prev =>
      prev.map(c => c.id === processingId ? { ...c, lensRun: "seasonal+social" } : c)
    );
    setProcessingId(null);
    setProcessingPct(0);
    setView("results");
  }

  function handleSelectCatalogue(id) {
    if (id === processingId) return;
    setActiveId(id);
    const cat = catalogues.find(c => c.id === id);
    setView(cat && cat.lensRun ? "results" : "empty");
  }

  const activeCat = catalogues.find(c => c.id === activeId) || null;

  let mainContent;
  if (view === "empty") {
    mainContent = <EmptyState onAdd={handleAdd} />;
  } else if (view === "upload") {
    mainContent = <Upload onCancel={handleCancelUpload} onIngest={handleIngest} />;
  } else if (view === "reading") {
    mainContent = <Reading catalogue={activeCat} onDone={handleReadingDone} />;
  } else if (view === "results" && activeCat) {
    mainContent = <Results catalogue={activeCat} />;
  } else {
    mainContent = <EmptyState onAdd={handleAdd} />;
  }

  return (
    <div className="min-h-screen flex flex-col" data-screen-label={"Prototype · " + view} style={{ background: "#0A0A0A" }}>
      <div className="flex flex-1 min-h-screen" style={{ maxWidth: 1440, margin: "0 auto", width: "100%" }}>
        <PSidebar
          catalogues={catalogues}
          activeId={activeId}
          processingId={processingId}
          processingPct={processingPct}
          onSelect={handleSelectCatalogue}
          onAdd={handleAdd}
        />
        <main className="flex-1 flex flex-col min-w-0">{mainContent}</main>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
