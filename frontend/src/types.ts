export type Lens = 'seasonal' | 'social';

export type PlatformKey = 'spotify' | 'instagram' | 'tiktok' | 'youtube';

export type Signals = Record<PlatformKey, number>;

export type SourceSummaries = Record<PlatformKey, string>;

export interface LensView {
  synth: string;
  reason: string;
  hot: boolean;
  signals: Signals;
  stats: Record<string, string>;
  sources?: SourceSummaries;
}

export interface Track {
  id: number;
  title: string;
  artist: string;
  year: number | null;
  lit: boolean;
  rank?: number;
  seasonal: LensView;
  social: LensView;
}

export interface Catalogue {
  id: number | string;
  name: string;
  filename?: string;
  tracks: number;
  addedAt?: number;
  lensRun?: string | null;
}

export interface StatusResponse {
  id: number;
  status: 'pending' | 'loading' | 'analyzing' | 'done' | 'error';
  pct: number;
  agent: string;
  step: string;
  error: string | null;
}

export interface ResultsResponse {
  catalogue: { id: number; name: string };
  tracks: Track[];
}

export interface UploadResponse {
  id: number;
  name: string;
  track_count: number;
  status: string;
}
