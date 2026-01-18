'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  FolderOpen,
  Inbox,
  Search,
  Settings,
  Plus,
} from 'lucide-react';
import { clsx } from 'clsx';
import { useState } from 'react';
import { AddModal } from './AddModal';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Entries', href: '/entries', icon: FolderOpen },
  { name: 'Proposals', href: '/proposals', icon: Inbox },
];

export function Sidebar() {
  const pathname = usePathname();
  const [showAddModal, setShowAddModal] = useState(false);

  return (
    <>
      <aside className="fixed left-0 top-0 h-screen w-64 bg-white border-r border-apple-gray-100 flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-apple-gray-100">
          <h1 className="text-xl font-semibold text-apple-gray-900">
            📦 mempocket
          </h1>
          <p className="text-sm text-apple-gray-400 mt-1">
            Your memory, organized
          </p>
        </div>

        {/* Quick Add Button */}
        <div className="p-4">
          <button
            onClick={() => setShowAddModal(true)}
            className="w-full btn-primary flex items-center justify-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Quick Add
          </button>
          <p className="text-xs text-apple-gray-400 text-center mt-2">
            ⌘K
          </p>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <ul className="space-y-1">
            {navigation.map((item) => {
              const isActive = pathname === item.href ||
                (item.href !== '/' && pathname.startsWith(item.href));
              const Icon = item.icon;

              return (
                <li key={item.name}>
                  <Link
                    href={item.href}
                    className={clsx(
                      'flex items-center gap-3 px-4 py-3 rounded-apple text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-apple-blue text-white'
                        : 'text-apple-gray-600 hover:bg-apple-gray-50'
                    )}
                  >
                    <Icon className="w-5 h-5" />
                    {item.name}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-apple-gray-100">
          <p className="text-xs text-apple-gray-400 text-center">
            3 boxes for everything<br />
            2 modes for life
          </p>
        </div>
      </aside>

      {/* Add Modal */}
      <AddModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
      />
    </>
  );
}
