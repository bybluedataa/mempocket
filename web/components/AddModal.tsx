'use client';

import { useState, useEffect, useRef } from 'react';
import { X, Sparkles, FolderPlus } from 'lucide-react';
import { clsx } from 'clsx';
import { quickAddAPI, entriesAPI } from '@/lib/api';
import { useRouter } from 'next/navigation';

interface AddModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type Mode = 'ai' | 'manual';

export function AddModal({ isOpen, onClose }: AddModalProps) {
  const [mode, setMode] = useState<Mode>('ai');
  const [content, setContent] = useState('');
  const [title, setTitle] = useState('');
  const [entity, setEntity] = useState<string>('project');
  const [context, setContext] = useState<string>('work');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const router = useRouter();

  // Keyboard shortcut
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        if (isOpen) {
          onClose();
        }
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    }
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Focus input when modal opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Reset state when modal closes
  useEffect(() => {
    if (!isOpen) {
      setContent('');
      setTitle('');
      setResult(null);
      setLoading(false);
    }
  }, [isOpen]);

  const handleSubmit = async () => {
    if (mode === 'ai' && !content.trim()) return;
    if (mode === 'manual' && !title.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      if (mode === 'ai') {
        const res = await quickAddAPI.add(content);
        if (res.proposals.length > 0) {
          setResult(`Created proposal! Check the Proposals page to review.`);
          setTimeout(() => {
            onClose();
            router.push('/proposals');
          }, 1500);
        } else {
          setResult('No proposals generated. Try adding more details.');
        }
      } else {
        const res = await entriesAPI.create({
          title,
          entity,
          context,
          content,
        });
        setResult(`Entry created!`);
        setTimeout(() => {
          onClose();
          router.push(`/entries/${res.id}`);
        }, 1000);
      }
    } catch (error) {
      setResult(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/30 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-xl bg-white rounded-apple-lg shadow-apple-lg animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-apple-gray-100">
          <div className="flex gap-2">
            <button
              onClick={() => setMode('ai')}
              className={clsx(
                'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
                mode === 'ai'
                  ? 'bg-apple-blue text-white'
                  : 'text-apple-gray-500 hover:bg-apple-gray-50'
              )}
            >
              <Sparkles className="w-4 h-4" />
              AI Classify
            </button>
            <button
              onClick={() => setMode('manual')}
              className={clsx(
                'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
                mode === 'manual'
                  ? 'bg-apple-blue text-white'
                  : 'text-apple-gray-500 hover:bg-apple-gray-50'
              )}
            >
              <FolderPlus className="w-4 h-4" />
              Manual
            </button>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-apple-gray-50 text-apple-gray-400"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4">
          {mode === 'ai' ? (
            <div>
              <textarea
                ref={inputRef}
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Describe what you want to remember...

Example: Meeting with Alice about Q3 budget planning, deadline June 30"
                className="input-field min-h-[120px] resize-none"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                    e.preventDefault();
                    handleSubmit();
                  }
                }}
              />
              <p className="text-xs text-apple-gray-400 mt-2">
                AI will classify this into the right entity and context
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Entry title"
                className="input-field"
              />

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-apple-gray-600 mb-2">
                    Entity
                  </label>
                  <div className="flex gap-2">
                    {['project', 'library', 'people'].map((e) => (
                      <button
                        key={e}
                        onClick={() => setEntity(e)}
                        className={clsx(
                          'px-3 py-1.5 rounded-lg text-sm font-medium capitalize',
                          entity === e
                            ? `badge-${e}`
                            : 'bg-apple-gray-50 text-apple-gray-500'
                        )}
                      >
                        {e}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-apple-gray-600 mb-2">
                    Context
                  </label>
                  <div className="flex gap-2">
                    {['work', 'life'].map((c) => (
                      <button
                        key={c}
                        onClick={() => setContext(c)}
                        className={clsx(
                          'px-3 py-1.5 rounded-lg text-sm font-medium capitalize',
                          context === c
                            ? `badge-${c}`
                            : 'bg-apple-gray-50 text-apple-gray-500'
                        )}
                      >
                        {c}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Content (optional, supports [[wiki links]])"
                className="input-field min-h-[80px] resize-none"
              />
            </div>
          )}

          {/* Result message */}
          {result && (
            <div
              className={clsx(
                'mt-4 p-3 rounded-apple text-sm',
                result.startsWith('Error')
                  ? 'bg-red-50 text-red-700'
                  : 'bg-green-50 text-green-700'
              )}
            >
              {result}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-4 border-t border-apple-gray-100">
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={loading || (mode === 'ai' ? !content.trim() : !title.trim())}
            className={clsx(
              'btn-primary',
              (loading || (mode === 'ai' ? !content.trim() : !title.trim())) &&
                'opacity-50 cursor-not-allowed'
            )}
          >
            {loading ? 'Processing...' : mode === 'ai' ? 'Add with AI' : 'Create Entry'}
          </button>
        </div>
      </div>
    </div>
  );
}
