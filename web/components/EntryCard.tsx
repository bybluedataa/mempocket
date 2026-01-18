'use client';

import Link from 'next/link';
import { clsx } from 'clsx';
import { Entry } from '@/lib/api';
import { Calendar, Link as LinkIcon } from 'lucide-react';

interface EntryCardProps {
  entry: Entry;
}

export function EntryCard({ entry }: EntryCardProps) {
  const entityColors: Record<string, string> = {
    project: 'badge-project',
    library: 'badge-library',
    people: 'badge-people',
  };

  const contextColors: Record<string, string> = {
    work: 'badge-work',
    life: 'badge-life',
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <Link href={`/entries/${entry.id}`}>
      <div className="bg-white rounded-apple p-4 shadow-apple card-hover cursor-pointer">
        {/* Header with badges */}
        <div className="flex items-start justify-between mb-3">
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
        </div>

        {/* Title */}
        <h3 className="text-lg font-semibold text-apple-gray-900 mb-2">
          {entry.title}
        </h3>

        {/* Content preview */}
        {entry.content && (
          <p className="text-sm text-apple-gray-500 line-clamp-2 mb-3">
            {entry.content.slice(0, 150)}
            {entry.content.length > 150 && '...'}
          </p>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between text-xs text-apple-gray-400">
          <div className="flex items-center gap-1">
            <Calendar className="w-3 h-3" />
            {formatDate(entry.created_at)}
          </div>
          {entry.links.length > 0 && (
            <div className="flex items-center gap-1">
              <LinkIcon className="w-3 h-3" />
              {entry.links.length} links
            </div>
          )}
        </div>
      </div>
    </Link>
  );
}
