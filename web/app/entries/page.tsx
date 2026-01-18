'use client';

import { useEffect, useState } from 'react';
import { entriesAPI, Entry } from '@/lib/api';
import { EntryCard } from '@/components/EntryCard';
import { SearchBar } from '@/components/SearchBar';
import { clsx } from 'clsx';

type EntityFilter = 'all' | 'project' | 'library' | 'people';
type ContextFilter = 'all' | 'work' | 'life';

export default function EntriesPage() {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [loading, setLoading] = useState(true);
  const [entityFilter, setEntityFilter] = useState<EntityFilter>('all');
  const [contextFilter, setContextFilter] = useState<ContextFilter>('all');

  const fetchEntries = async () => {
    setLoading(true);
    try {
      const filters: { entity?: string; context?: string } = {};
      if (entityFilter !== 'all') filters.entity = entityFilter;
      if (contextFilter !== 'all') filters.context = contextFilter;

      const res = await entriesAPI.list(filters);
      setEntries(res.entries);
    } catch (error) {
      console.error('Failed to fetch entries:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEntries();
  }, [entityFilter, contextFilter]);

  const entityButtons: { value: EntityFilter; label: string; className: string }[] = [
    { value: 'all', label: 'All', className: 'bg-apple-gray-100 text-apple-gray-700' },
    { value: 'project', label: 'Projects', className: 'badge-project' },
    { value: 'library', label: 'Library', className: 'badge-library' },
    { value: 'people', label: 'People', className: 'badge-people' },
  ];

  const contextButtons: { value: ContextFilter; label: string; className: string }[] = [
    { value: 'all', label: 'All', className: 'bg-apple-gray-100 text-apple-gray-700' },
    { value: 'work', label: 'Work', className: 'badge-work' },
    { value: 'life', label: 'Life', className: 'badge-life' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-apple-gray-900">Entries</h1>
          <p className="text-apple-gray-500 mt-1">
            {entries.length} {entries.length === 1 ? 'entry' : 'entries'}
          </p>
        </div>
        <SearchBar />
      </div>

      {/* Filters */}
      <div className="bg-white rounded-apple p-4 shadow-apple">
        <div className="flex flex-wrap items-center gap-6">
          {/* Entity filter */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-apple-gray-500">Entity:</span>
            <div className="flex gap-1">
              {entityButtons.map((btn) => (
                <button
                  key={btn.value}
                  onClick={() => setEntityFilter(btn.value)}
                  className={clsx(
                    'px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
                    entityFilter === btn.value
                      ? btn.className
                      : 'bg-transparent text-apple-gray-400 hover:bg-apple-gray-50'
                  )}
                >
                  {btn.label}
                </button>
              ))}
            </div>
          </div>

          {/* Context filter */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-apple-gray-500">Context:</span>
            <div className="flex gap-1">
              {contextButtons.map((btn) => (
                <button
                  key={btn.value}
                  onClick={() => setContextFilter(btn.value)}
                  className={clsx(
                    'px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
                    contextFilter === btn.value
                      ? btn.className
                      : 'bg-transparent text-apple-gray-400 hover:bg-apple-gray-50'
                  )}
                >
                  {btn.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Entries grid */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-apple-gray-400">Loading...</div>
        </div>
      ) : entries.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {entries.map((entry) => (
            <EntryCard key={entry.id} entry={entry} />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-apple p-8 text-center shadow-apple">
          <p className="text-apple-gray-400 mb-4">No entries found</p>
          <p className="text-sm text-apple-gray-500">
            {entityFilter !== 'all' || contextFilter !== 'all'
              ? 'Try adjusting your filters'
              : 'Use Quick Add (⌘K) to create your first entry'}
          </p>
        </div>
      )}
    </div>
  );
}
