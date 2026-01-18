'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { entriesAPI, Entry } from '@/lib/api';
import { MarkdownView } from '@/components/MarkdownView';
import { clsx } from 'clsx';
import {
  ArrowLeft,
  Calendar,
  Clock,
  Link as LinkIcon,
  Trash2,
  Edit3,
} from 'lucide-react';
import Link from 'next/link';

export default function EntryDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [entry, setEntry] = useState<Entry | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [editContent, setEditContent] = useState('');
  const [saving, setSaving] = useState(false);

  const id = params.id as string;

  useEffect(() => {
    const fetchEntry = async () => {
      try {
        const data = await entriesAPI.get(id);
        setEntry(data);
        setEditContent(data.content || '');
      } catch (error) {
        console.error('Failed to fetch entry:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchEntry();
  }, [id]);

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this entry?')) return;

    try {
      await entriesAPI.delete(id);
      router.push('/entries');
    } catch (error) {
      console.error('Failed to delete:', error);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await entriesAPI.update(id, editContent);
      setEntry({ ...entry!, content: editContent });
      setEditing(false);
    } catch (error) {
      console.error('Failed to save:', error);
    } finally {
      setSaving(false);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const entityColors: Record<string, string> = {
    project: 'badge-project',
    library: 'badge-library',
    people: 'badge-people',
  };

  const contextColors: Record<string, string> = {
    work: 'badge-work',
    life: 'badge-life',
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-apple-gray-400">Loading...</div>
      </div>
    );
  }

  if (!entry) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-apple-gray-900 mb-2">
          Entry not found
        </h2>
        <Link href="/entries" className="text-apple-blue hover:underline">
          Back to entries
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Back button */}
      <Link
        href="/entries"
        className="inline-flex items-center gap-2 text-apple-gray-500 hover:text-apple-gray-700 mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to entries
      </Link>

      {/* Header */}
      <div className="bg-white rounded-apple p-6 shadow-apple mb-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex gap-2">
            <span
              className={clsx(
                'px-2 py-0.5 rounded-md text-xs font-medium capitalize',
                entityColors[entry.entity]
              )}
            >
              {entry.entity}
            </span>
            <span
              className={clsx(
                'px-2 py-0.5 rounded-md text-xs font-medium capitalize',
                contextColors[entry.context]
              )}
            >
              {entry.context}
            </span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setEditing(!editing)}
              className="p-2 rounded-lg hover:bg-apple-gray-50 text-apple-gray-400 hover:text-apple-gray-600"
            >
              <Edit3 className="w-4 h-4" />
            </button>
            <button
              onClick={handleDelete}
              className="p-2 rounded-lg hover:bg-red-50 text-apple-gray-400 hover:text-red-500"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        <h1 className="text-2xl font-semibold text-apple-gray-900 mb-4">
          {entry.title}
        </h1>

        <div className="flex items-center gap-4 text-sm text-apple-gray-400">
          <div className="flex items-center gap-1">
            <Calendar className="w-4 h-4" />
            {formatDate(entry.created_at)}
          </div>
          {entry.links.length > 0 && (
            <div className="flex items-center gap-1">
              <LinkIcon className="w-4 h-4" />
              {entry.links.length} links
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="bg-white rounded-apple p-6 shadow-apple mb-6">
        <h2 className="text-lg font-semibold text-apple-gray-900 mb-4">
          Content
        </h2>

        {editing ? (
          <div>
            <textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              className="input-field min-h-[200px] font-mono text-sm"
              placeholder="Enter content (supports Markdown and [[wiki links]])"
            />
            <div className="flex justify-end gap-3 mt-4">
              <button
                onClick={() => {
                  setEditing(false);
                  setEditContent(entry.content || '');
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={saving}
                className="btn-primary"
              >
                {saving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        ) : entry.content ? (
          <MarkdownView content={entry.content} />
        ) : (
          <p className="text-apple-gray-400 italic">No content yet</p>
        )}
      </div>

      {/* Links */}
      {entry.links.length > 0 && (
        <div className="bg-white rounded-apple p-6 shadow-apple mb-6">
          <h2 className="text-lg font-semibold text-apple-gray-900 mb-4">
            Links
          </h2>
          <div className="flex flex-wrap gap-2">
            {entry.links.map((link) => (
              <span
                key={link}
                className="px-3 py-1 bg-apple-blue/10 text-apple-blue rounded-full text-sm"
              >
                [[{link}]]
              </span>
            ))}
          </div>
        </div>
      )}

      {/* History */}
      {entry.history && entry.history.length > 0 && (
        <div className="bg-white rounded-apple p-6 shadow-apple">
          <h2 className="text-lg font-semibold text-apple-gray-900 mb-4">
            History
          </h2>
          <ul className="space-y-3">
            {entry.history.map((h, i) => (
              <li
                key={i}
                className="flex items-center gap-3 text-sm text-apple-gray-500"
              >
                <Clock className="w-4 h-4" />
                <span className="capitalize font-medium">{h.action}</span>
                <span className="text-apple-gray-400">
                  {formatDate(h.timestamp)}
                </span>
                {h.details && (
                  <span className="text-apple-gray-400">- {h.details}</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
