'use client';

import { useEffect, useState } from 'react';
import { statusAPI, entriesAPI, proposalsAPI, SystemStatus, Entry, Proposal } from '@/lib/api';
import { EntryCard } from '@/components/EntryCard';
import { ProposalCard } from '@/components/ProposalCard';
import { SearchBar } from '@/components/SearchBar';
import { FolderOpen, Users, BookOpen, Inbox } from 'lucide-react';

export default function Dashboard() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [recentEntries, setRecentEntries] = useState<Entry[]>([]);
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [statusRes, entriesRes, proposalsRes] = await Promise.all([
        statusAPI.get(),
        entriesAPI.list(),
        proposalsAPI.list(),
      ]);
      setStatus(statusRes);
      setRecentEntries(entriesRes.entries.slice(0, 6));
      setProposals(proposalsRes.proposals.slice(0, 3));
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-apple-gray-400">Loading...</div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-apple-gray-900">Dashboard</h1>
          <p className="text-apple-gray-500 mt-1">Your personal context at a glance</p>
        </div>
        <SearchBar />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard
          icon={<FolderOpen className="w-6 h-6" />}
          label="Projects"
          value={status?.by_entity.project || 0}
          color="blue"
        />
        <StatCard
          icon={<BookOpen className="w-6 h-6" />}
          label="Library"
          value={status?.by_entity.library || 0}
          color="purple"
        />
        <StatCard
          icon={<Users className="w-6 h-6" />}
          label="People"
          value={status?.by_entity.people || 0}
          color="green"
        />
        <StatCard
          icon={<Inbox className="w-6 h-6" />}
          label="Pending"
          value={status?.pending_proposals || 0}
          color="orange"
        />
      </div>

      {/* Pending Proposals */}
      {proposals.length > 0 && (
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-apple-gray-900">
              Pending Proposals
            </h2>
            <a
              href="/proposals"
              className="text-sm text-apple-blue hover:underline"
            >
              View all
            </a>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {proposals.map((proposal) => (
              <ProposalCard
                key={proposal.id}
                proposal={proposal}
                onUpdate={fetchData}
              />
            ))}
          </div>
        </section>
      )}

      {/* Recent Entries */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-apple-gray-900">
            Recent Entries
          </h2>
          <a
            href="/entries"
            className="text-sm text-apple-blue hover:underline"
          >
            View all
          </a>
        </div>
        {recentEntries.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recentEntries.map((entry) => (
              <EntryCard key={entry.id} entry={entry} />
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-apple p-8 text-center shadow-apple">
            <p className="text-apple-gray-400 mb-4">No entries yet</p>
            <p className="text-sm text-apple-gray-500">
              Use Quick Add (⌘K) to create your first entry
            </p>
          </div>
        )}
      </section>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
  color: 'blue' | 'purple' | 'green' | 'orange';
}) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    purple: 'bg-purple-50 text-purple-600',
    green: 'bg-green-50 text-green-600',
    orange: 'bg-orange-50 text-orange-600',
  };

  return (
    <div className="bg-white rounded-apple p-4 shadow-apple">
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-apple ${colorClasses[color]}`}>
          {icon}
        </div>
        <div>
          <p className="text-2xl font-semibold text-apple-gray-900">{value}</p>
          <p className="text-sm text-apple-gray-500">{label}</p>
        </div>
      </div>
    </div>
  );
}
