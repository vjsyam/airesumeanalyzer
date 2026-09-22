const API_BASE = '/api';

export const getStoredApiKey = () => {
  return localStorage.getItem('gemini_api_key') || '';
};

export const setStoredApiKey = (key) => {
  if (key) {
    localStorage.setItem('gemini_api_key', key.trim());
  } else {
    localStorage.removeItem('gemini_api_key');
  }
};

export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`Status ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Health check failed', err);
    return { status: 'offline', error: err.message };
  }
}

export async function fetchSampleData() {
  const res = await fetch(`${API_BASE}/sample-data`);
  if (!res.ok) throw new Error('Failed to load sample data');
  return await res.json();
}

export async function analyzeResume({ file, jobDescription, sampleResumeId, rawResumeText }) {
  const formData = new FormData();
  formData.append('job_description', jobDescription);
  
  if (file) {
    formData.append('file', file);
  }
  if (sampleResumeId) {
    formData.append('sample_resume_id', sampleResumeId);
  }
  if (rawResumeText) {
    formData.append('raw_resume_text', rawResumeText);
  }

  const apiKey = getStoredApiKey();
  const headers = {};
  if (apiKey) {
    headers['X-Gemini-Api-Key'] = apiKey;
  }

  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers,
    body: formData,
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Analysis failed with status ${res.status}`);
  }

  return await res.json();
}

export async function generateCoverLetter({ resumeText, jobDescription, tone = 'direct', candidateName = 'Applicant' }) {
  const apiKey = getStoredApiKey();
  const headers = { 'Content-Type': 'application/json' };
  if (apiKey) {
    headers['X-Gemini-Api-Key'] = apiKey;
  }

  const res = await fetch(`${API_BASE}/cover-letter`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      resume_text: resumeText,
      job_description: jobDescription,
      tone,
      candidate_name: candidateName,
    }),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || 'Cover letter generation failed');
  }

  return await res.json();
}

export async function exportDocx({ coverLetter, candidateName = 'Applicant' }) {
  const res = await fetch(`${API_BASE}/export/docx`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      cover_letter: coverLetter,
      candidate_name: candidateName,
    }),
  });

  if (!res.ok) throw new Error('Failed to generate docx export');

  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${candidateName.replace(/\s+/g, '_')}_Cover_Letter.docx`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}
