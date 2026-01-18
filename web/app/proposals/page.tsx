'use client';

import { useEffect, useState } from 'react';
import { proposalsAPI, Proposal } from '@/lib/api';
import { ProposalCard } from '@/components/ProposalCard';
import { Inbox } from 'lucide-react';

export default function ProposalsPage() {
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchProposals = async () => {
    try {
      const res = await proposalsAPI.list();
      setProposals(res.proposals);
    } catch (error) {
      console.error('Failed to fetch proposals:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProposals();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-apple-gray-400">Loading...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-semibold text-apple-gray-900">Proposals</h1>
        <p className="text-apple-gray-500 mt-1">
          Review AI suggestions before adding to your memory
        </p>
      </div>

      {/* Proposals list */}
      {proposals.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {proposals.map((proposal) => (
            <ProposalCard
              key={proposal.id}
              proposal={proposal}
              onUpdate={fetchProposals}
            />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-apple p-12 text-center shadow-apple">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-apple-gray-100 mb-4">
            <Inbox className="w-8 h-8 text-apple-gray-400" />
          </div>
          <h2 className="text-xl font-semibold text-apple-gray-900 mb-2">
            No pending proposals
          </h2>
          <p className="text-apple-gray-500 max-w-md mx-auto">
            Use Quick Add (⌘K) with AI classification to let the agent suggest
            entries for you. You&apos;ll review and approve them here.
          </p>
        </div>
      )}
    </div>
  );
}
