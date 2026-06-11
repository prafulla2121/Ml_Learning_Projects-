'use client';

import { useState } from 'react';
import Link from 'next/link';

type PlatformId = 'qbo' | 'xero' | 'netsuite' | 'dynamics';

export default function SettingsPage() {
  const [platformStatus, setPlatformStatus] = useState<Record<PlatformId, string>>({
    qbo: 'connected',
    xero: 'disconnected',
    netsuite: 'disconnected',
    dynamics: 'disconnected'
  });

  const platforms: {id: PlatformId, name: string, color: string}[] = [
    { id: 'qbo', name: 'QuickBooks Online', color: 'green' },
    { id: 'xero', name: 'Xero', color: 'blue' },
    { id: 'netsuite', name: 'NetSuite', color: 'orange' },
    { id: 'dynamics', name: 'Dynamics 365 BC', color: 'purple' },
  ];

  return (
    <div className="flex min-h-screen bg-gray-50">
      <aside className="w-64 bg-white border-r flex flex-col">
        <div className="p-6 border-b">
          <h1 className="text-2xl font-bold text-blue-600">AccountOS</h1>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <Link href="/dashboard" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Dashboard</Link>
          <Link href="/settings" className="block px-4 py-2 text-blue-600 bg-blue-50 rounded-lg font-medium">Settings</Link>
        </nav>
      </aside>

      <main className="flex-1 p-8">
        <h1 className="text-3xl font-bold mb-8 text-gray-900">Settings</h1>

        <div className="max-w-4xl space-y-8">
          <section className="bg-white border p-6 rounded-xl shadow-sm">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">Accounting Platforms</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {platforms.map(p => (
                <div key={p.id} className="flex items-center justify-between p-4 border rounded-lg hover:border-blue-300 transition-colors">
                    <div className="flex items-center gap-4">
                        <div className={`w-10 h-10 bg-${p.color}-50 rounded-lg flex items-center justify-center text-${p.color}-600 font-bold`}>
                            {p.name.substring(0, 2).toUpperCase()}
                        </div>
                        <div>
                            <p className="font-semibold text-gray-900">{p.name}</p>
                            <p className="text-xs text-gray-500">Status: {platformStatus[p.id]}</p>
                        </div>
                    </div>
                    <button className="bg-blue-600 text-white px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-blue-700 shadow-sm">
                        {platformStatus[p.id] === 'connected' ? 'Manage' : 'Connect'}
                    </button>
                </div>
              ))}
            </div>
          </section>

          <section className="bg-white border p-6 rounded-xl shadow-sm">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">Language & Region</h2>
            <div className="flex items-center gap-4">
                <select className="border p-2 rounded-lg bg-white shadow-sm w-48">
                    <option value="en">English (US)</option>
                    <option value="hi">Hindi (हिन्दी)</option>
                    <option value="gu">Gujarati (ગુજરાતી)</option>
                </select>
                <p className="text-sm text-gray-500 italic">Select your preferred interface language.</p>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
