'use client';

import { useState, useEffect, useRef } from 'react';
import { Search, X } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { clsx } from 'clsx';
import { searchAPI, Entry } from '@/lib/api';

export function SearchBar() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Entry[]>([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  // Keyboard shortcut
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === '/') {
        e.preventDefault();
        setIsOpen(true);
      }
      if (e.key === 'Escape') {
        setIsOpen(false);
        setQuery('');
        setResults([]);
      }
    }
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Focus input when opening
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Search as you type
  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await searchAPI.search(query);
        setResults(res.results);
      } catch (error) {
        console.error('Search failed:', error);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  const handleSelect = (entry: Entry) => {
    router.push(`/entries/${entry.id}`);
    setIsOpen(false);
    setQuery('');
    setResults([]);
  };

  const entityColors: Record<string, string> = {
    project: 'badge-project',
    library: 'badge-library',
    people: 'badge-people',
  };

  return (
    <>
      {/* Search trigger */}
      <button
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-2 px-4 py-2 bg-white rounded-apple shadow-apple text-apple-gray-400 hover:shadow-apple-md transition-shadow"
      >
        <Search className="w-4 h-4" />
        <span className="text-sm">Search...</span>
        <kbd className="ml-8 px-1.5 py-0.5 text-xs bg-apple-gray-100 rounded">
          ⌘/
        </kbd>
      </button>

      {/* Search modal */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]">
          <div
            className="absolute inset-0 bg-black/30 backdrop-blur-sm"
            onClick={() => {
              setIsOpen(false);
              setQuery('');
              setResults([]);
            }}
          />

          <div className="relative w-full max-w-xl bg-white rounded-apple-lg shadow-apple-lg animate-fade-in">
            {/* Search input */}
            <div className="flex items-center gap-3 p-4 border-b border-apple-gray-100">
              <Search className="w-5 h-5 text-apple-gray-400" />
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search entries..."
                className="flex-1 outline-none text-lg"
              />
              {query && (
                <button
                  onClick={() => {
                    setQuery('');
                    setResults([]);
                  }}
                  className="p-1 rounded-lg hover:bg-apple-gray-50"
                >
                  <X className="w-4 h-4 text-apple-gray-400" />
                </button>
              )}
            </div>

            {/* Results */}
            <div className="max-h-[60vh] overflow-y-auto">
              {loading && (
                <div className="p-4 text-center text-apple-gray-400">
                  Searching...
                </div>
              )}

              {!loading && query && results.length === 0 && (
                <div className="p-4 text-center text-apple-gray-400">
                  No results found
                </div>
              )}

              {!loading && results.length > 0 && (
                <ul className="p-2">
                  {results.map((entry) => (
                    <li key={entry.id}>
                      <button
                        onClick={() => handleSelect(entry)}
                        className="w-full flex items-center gap-3 p-3 rounded-apple hover:bg-apple-gray-50 text-left"
                      >
                        <span
                          className={clsx(
                            'px-2 py-0.5 rounded-md text-xs font-medium capitalize',
                            entityColors[entry.entity]
                          )}
                        >
                          {entry.entity}
                        </span>
                        <span className="flex-1 font-medium text-apple-gray-900">
                          {entry.title}
                        </span>
                      </button>
                    </li>
                  ))}
                </ul>
              )}

              {!query && (
                <div className="p-4 text-center text-sm text-apple-gray-400">
                  Start typing to search
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
