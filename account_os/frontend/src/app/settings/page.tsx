'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function SettingsPage() {
  const [isConnecting, setIsConnecting] = useState(false);
  const [platformStatus, setPlatformStatus] = useState({
    qbo: 'disconnected',
    xero: 'disconnected'
  });

  const handleConnectQBO = async () => {
    setIsConnecting(true);
    try {
      const response = await fetch('http://localhost:8000/auth/qbo/authorize?client_id=123');
      const data = await response.json();
      if (data.auth_url) {
        window.location.href = data.auth_url;
      }
    } catch (error) {
      console.error('Failed to connect to QBO', error);
      setIsConnecting(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar (Shared) */}
      <aside className="w-64 bg-white border-r flex flex-col">
        <div className="p-6 border-b">
          <h1 className="text-2xl font-bold text-blue-600">AccountOS</h1>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <Link href="/dashboard" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Dashboard</Link>
          <Link href="/approvals" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Approval Queue</Link>
          <Link href="/transactions" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Transactions</Link>
          <Link href="/settings" className="block px-4 py-2 text-blue-600 bg-blue-50 rounded-lg font-medium">Settings</Link>
        </nav>
      </aside>

      <main className="flex-1 p-8">
        <h1 className="text-3xl font-bold mb-8 text-gray-900">Settings</h1>

        <div className="max-w-3xl space-y-8">
          <section className="bg-white border p-6 rounded-xl shadow-sm">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">Accounting Platforms</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 border rounded-lg hover:border-blue-300 transition-colors">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-green-50 rounded-lg flex items-center justify-center text-green-600 font-bold">QB</div>
                  <div>
                    <p className="font-semibold text-gray-900">QuickBooks Online</p>
                    <p className={`text-xs ${
                      platformStatus.qbo === 'connected' ? 'text-green-600' : 'text-gray-500'
                    }`}>
                      Status: {platformStatus.qbo}
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleConnectQBO}
                  disabled={isConnecting}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:bg-blue-300 shadow-sm"
                >
                  {isConnecting ? 'Connecting...' : 'Connect'}
                </button>
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg hover:border-blue-300 transition-colors">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center text-blue-600 font-bold">X</div>
                  <div>
                    <p className="font-semibold text-gray-900">Xero</p>
                    <p className="text-xs text-gray-500">Status: {platformStatus.xero}</p>
                  </div>
                </div>
                <button className="bg-blue-600 text-white px-6 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 shadow-sm">
                  Connect
                </button>
              </div>
            </div>
          </section>

          <section className="bg-white border p-6 rounded-xl shadow-sm">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-800">GL Mapping Rules</h2>
              <button className="text-blue-600 text-sm font-bold hover:underline">+ New Rule</button>
            </div>
            <div className="space-y-3">
              <div className="p-4 border rounded-lg bg-gray-50 flex justify-between items-center group">
                <div>
                  <p className="font-semibold text-gray-900">Amazon → 6200 Office Supplies</p>
                  <p className="text-xs text-gray-500">Matches 'Amazon' in Vendor field</p>
                </div>
                <button className="text-red-500 opacity-0 group-hover:opacity-100 transition-opacity text-sm font-medium">Delete</button>
              </div>
            </div>
          </section>

          <section className="bg-white border p-6 rounded-xl shadow-sm">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">Workflow Overrides</h2>
            <div className="p-4 border rounded-lg flex items-center justify-between">
              <div>
                <p className="font-semibold text-gray-900">High-Value Approval</p>
                <p className="text-xs text-gray-500">Transactions over $5,000.00 require manual sign-off</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded-full font-bold">ACTIVE</span>
                <button className="text-gray-400 hover:text-gray-600">Edit</button>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
