import type { ResultsResponse, StatusResponse, UploadResponse } from '../types';

export async function uploadCatalogue(file: File, name: string): Promise<UploadResponse> {
  const form = new FormData();
  form.append('file', file);
  form.append('name', name);
  const resp = await fetch('/api/catalogues', { method: 'POST', body: form });
  if (!resp.ok) throw new Error('Upload failed: ' + resp.status);
  return resp.json();
}

export async function fetchStatus(id: number): Promise<StatusResponse> {
  const r = await fetch(`/api/catalogues/${id}/status`);
  if (!r.ok) throw new Error('HTTP ' + r.status);
  return r.json();
}

export async function fetchResults(id: number): Promise<ResultsResponse> {
  const r = await fetch(`/api/catalogues/${id}/results`);
  if (!r.ok) throw new Error('HTTP ' + r.status);
  return r.json();
}
