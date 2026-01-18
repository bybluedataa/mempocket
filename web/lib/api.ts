const API_BASE = '/api';

export interface Entry {
  id: string;
  title: string;
  entity: 'project' | 'library' | 'people';
  context: 'work' | 'life';
  content: string;
  links: string[];
  created_at: string;
  updated_at: string;
  history?: {
    action: string;
    timestamp: string;
    details?: string;
  }[];
}

export interface Proposal {
  id: string;
  type: string;
  status: string;
  confidence: number;
  reason: string;
  created_at: string;
  suggested: {
    title: string;
    entity: string;
    context: string;
    content: string;
  };
  evidence: {
    source_input: string;
    extracted_from: string;
  };
}

export interface SystemStatus {
  total_entries: number;
  by_entity: {
    project: number;
    library: number;
    people: number;
  };
  by_context: {
    work: number;
    life: number;
  };
  pending_proposals: number;
  inbox_items: number;
}

// Fetch wrapper with error handling
async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.detail || 'API request failed');
  }

  return res.json();
}

// Entries API
export const entriesAPI = {
  list: async (filters?: { entity?: string; context?: string }) => {
    const params = new URLSearchParams();
    if (filters?.entity) params.set('entity', filters.entity);
    if (filters?.context) params.set('context', filters.context);
    const query = params.toString() ? `?${params}` : '';
    return fetchAPI<{ entries: Entry[] }>(`/entries${query}`);
  },

  get: async (id: string) => {
    return fetchAPI<Entry>(`/entries/${id}`);
  },

  create: async (data: {
    title: string;
    entity: string;
    context: string;
    content?: string;
  }) => {
    return fetchAPI<{ id: string; message: string }>('/entries', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  update: async (id: string, content: string) => {
    return fetchAPI<{ id: string; message: string }>(`/entries/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ content }),
    });
  },

  delete: async (id: string) => {
    return fetchAPI<{ message: string }>(`/entries/${id}`, {
      method: 'DELETE',
    });
  },

  getLinks: async (id: string) => {
    return fetchAPI<{ links: string[] }>(`/entries/${id}/links`);
  },

  getBacklinks: async (id: string) => {
    return fetchAPI<{ backlinks: string[] }>(`/entries/${id}/backlinks`);
  },
};

// Quick Add API
export const quickAddAPI = {
  add: async (content: string) => {
    return fetchAPI<{
      run_id: string;
      input_id: string;
      proposals: string[];
      steps: { stage: string; result: string }[];
      flags: string[];
    }>('/add', {
      method: 'POST',
      body: JSON.stringify({ content }),
    });
  },
};

// Proposals API
export const proposalsAPI = {
  list: async () => {
    return fetchAPI<{ proposals: Proposal[] }>('/proposals');
  },

  get: async (id: string) => {
    return fetchAPI<Proposal>(`/proposals/${id}`);
  },

  approve: async (id: string) => {
    return fetchAPI<{ message: string; entry_id: string }>(
      `/proposals/${id}/approve`,
      { method: 'POST' }
    );
  },

  reject: async (id: string, reason?: string) => {
    return fetchAPI<{ message: string }>(`/proposals/${id}/reject`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    });
  },
};

// Search API
export const searchAPI = {
  search: async (query: string) => {
    return fetchAPI<{
      query: string;
      results: Entry[];
    }>(`/search?q=${encodeURIComponent(query)}`);
  },
};

// Status API
export const statusAPI = {
  get: async () => {
    return fetchAPI<SystemStatus>('/status');
  },
};
