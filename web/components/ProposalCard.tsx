'use client';

import { useState } from 'react';
import { clsx } from 'clsx';
import { Proposal, proposalsAPI } from '@/lib/api';
import { Check, X, Sparkles } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface ProposalCardProps {
  proposal: Proposal;
  onUpdate: () => void;
}

export function ProposalCard({ proposal, onUpdate }: ProposalCardProps) {
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const entityColors: Record<string, string> = {
    project: 'badge-project',
    library: 'badge-library',
    people: 'badge-people',
  };

  const contextColors: Record<string, string> = {
    work: 'badge-work',
    life: 'badge-life',
  };

  const handleApprove = async () => {
    setLoading(true);
    try {
      const res = await proposalsAPI.approve(proposal.id);
      onUpdate();
      router.push(`/entries/${res.entry_id}`);
    } catch (error) {
      console.error('Failed to approve:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    setLoading(true);
    try {
      await proposalsAPI.reject(proposal.id);
      onUpdate();
    } catch (error) {
      console.error('Failed to reject:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-apple p-4 shadow-apple">
      {/* AI indicator */}
      <div className="flex items-center gap-2 mb-3 text-apple-gray-400">
        <Sparkles className="w-4 h-4" />
        <span className="text-xs">AI Suggestion</span>
        <span className="text-xs">•</span>
        <span className="text-xs">{Math.round(proposal.confidence * 100)}% confidence</span>
      </div>

      {/* Suggested entry */}
      <div className="bg-apple-gray-50 rounded-apple p-4 mb-4">
        <div className="flex gap-2 mb-2">
          <span
            className={clsx(
              'px-2 py-0.5 rounded-md text-xs font-medium capitalize',
              entityColors[proposal.suggested.entity]
            )}
          >
            {proposal.suggested.entity}
          </span>
          <span
            className={clsx(
              'px-2 py-0.5 rounded-md text-xs font-medium capitalize',
              contextColors[proposal.suggested.context]
            )}
          >
            {proposal.suggested.context}
          </span>
        </div>

        <h3 className="text-lg font-semibold text-apple-gray-900 mb-2">
          {proposal.suggested.title}
        </h3>

        {proposal.suggested.content && (
          <p className="text-sm text-apple-gray-600">
            {proposal.suggested.content}
          </p>
        )}
      </div>

      {/* Reason */}
      <p className="text-sm text-apple-gray-500 mb-4">
        <span className="font-medium">Reason:</span> {proposal.reason}
      </p>

      {/* Evidence */}
      <div className="text-xs text-apple-gray-400 mb-4">
        <span className="font-medium">From:</span>{' '}
        {proposal.evidence.extracted_from.slice(0, 100)}
        {proposal.evidence.extracted_from.length > 100 && '...'}
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        <button
          onClick={handleApprove}
          disabled={loading}
          className={clsx(
            'flex-1 flex items-center justify-center gap-2 py-2 rounded-apple font-medium text-sm',
            'bg-apple-green text-white hover:bg-green-600',
            loading && 'opacity-50 cursor-not-allowed'
          )}
        >
          <Check className="w-4 h-4" />
          Approve
        </button>
        <button
          onClick={handleReject}
          disabled={loading}
          className={clsx(
            'flex-1 flex items-center justify-center gap-2 py-2 rounded-apple font-medium text-sm',
            'bg-apple-gray-100 text-apple-gray-600 hover:bg-apple-gray-200',
            loading && 'opacity-50 cursor-not-allowed'
          )}
        >
          <X className="w-4 h-4" />
          Reject
        </button>
      </div>
    </div>
  );
}
