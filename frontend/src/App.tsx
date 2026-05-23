import { useEffect, useRef, useState } from 'react';

import { uploadCatalogue } from './api/catalogues';
import Empty from './components/Empty';
import Reading from './components/Reading';
import Results from './components/Results';
import Sidebar from './components/Sidebar';
import Upload from './components/Upload';
import type { IngestPayload } from './components/Upload';
import type { Catalogue } from './types';

type View = 'empty' | 'upload' | 'reading' | 'results';

interface ProgressEventDetail {
  id: number | string;
  pct: number;
}

export default function App() {
  const [view, setView] = useState<View>('empty');
  const [catalogues, setCatalogues] = useState<Catalogue[]>([]);
  const [activeId, setActiveId] = useState<number | string | null>(null);
  const [processingId, setProcessingId] = useState<number | string | null>(null);
  const [processingPct, setProcessingPct] = useState(0);
  const idRef = useRef(1);

  // Listen for progress events from <Reading />
  useEffect(() => {
    function onProgress(e: Event) {
      const detail = (e as CustomEvent<ProgressEventDetail>).detail;
      if (!detail) return;
      if (detail.id === processingId) setProcessingPct(detail.pct);
    }
    window.addEventListener('catalyst:processing-progress', onProgress);
    return () => window.removeEventListener('catalyst:processing-progress', onProgress);
  }, [processingId]);

  // Keyboard shortcuts
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      const target = e.target as HTMLElement | null;
      if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA')) return;
      if (e.key === 'n' || e.key === 'N') {
        if (view !== 'upload' && view !== 'reading') setView('upload');
      } else if (e.key === 'Escape') {
        if (view === 'upload') setView(activeId ? 'results' : 'empty');
      }
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [view, activeId]);

  function handleAdd() { setView('upload'); }
  function handleCancelUpload() { setView(activeId ? 'results' : 'empty'); }

  async function handleIngest({ name, filename, size, file }: IngestPayload) {
    const localId = 'c-' + (idRef.current++);
    const estTracks = Math.max(24, Math.min(1000, Math.round((size || 12000) / 100)));
    const pending: Catalogue = { id: localId, name, filename, tracks: estTracks, addedAt: Date.now(), lensRun: null };
    setCatalogues(prev => [pending, ...prev]);
    setActiveId(localId);
    setProcessingId(localId);
    setProcessingPct(0);
    setView('reading');

    if (!file) return;
    try {
      const data = await uploadCatalogue(file, name);
      setCatalogues(prev => prev.map(c =>
        c.id === localId
          ? { ...c, id: data.id, tracks: data.track_count || estTracks }
          : c
      ));
      setActiveId(data.id);
      setProcessingId(data.id);
    } catch (err) {
      console.error('Catalogue upload failed:', err);
      // Leave the timer-driven demo mode intact — Reading falls back
    }
  }

  function handleReadingDone() {
    setCatalogues(prev =>
      prev.map(c => c.id === processingId ? { ...c, lensRun: 'seasonal+social' } : c)
    );
    setProcessingId(null);
    setProcessingPct(0);
    setView('results');
  }

  function handleSelectCatalogue(id: number | string) {
    if (id === processingId) return;
    setActiveId(id);
    const cat = catalogues.find(c => c.id === id);
    setView(cat && cat.lensRun ? 'results' : 'empty');
  }

  const activeCat = catalogues.find(c => c.id === activeId) || null;

  let mainContent;
  if (view === 'empty') {
    mainContent = <Empty onAdd={handleAdd} />;
  } else if (view === 'upload') {
    mainContent = <Upload onCancel={handleCancelUpload} onIngest={handleIngest} />;
  } else if (view === 'reading') {
    mainContent = <Reading catalogue={activeCat} onDone={handleReadingDone} />;
  } else if (view === 'results' && activeCat) {
    mainContent = <Results catalogue={activeCat} />;
  } else {
    mainContent = <Empty onAdd={handleAdd} />;
  }

  return (
    <div className="min-h-screen flex flex-col" data-screen-label={'Prototype · ' + view} style={{ background: '#0A0A0A' }}>
      <div className="flex flex-1 min-h-screen" style={{ maxWidth: 1440, margin: '0 auto', width: '100%' }}>
        <Sidebar
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
