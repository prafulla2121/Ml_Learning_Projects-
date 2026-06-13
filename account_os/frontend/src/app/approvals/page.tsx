'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function ApprovalQueuePage() {
  const [syncing, setSyncing] = useState<string | null>(null);
  const [pendingTransactions, setPendingTransactions] = useState<any[]>([]);

  useEffect(() => {
    const fetchPending = async () => {
        try {
            const API_BASE_URL = (await import('../config')).default;
            const res = await fetch(`${API_BASE_URL}/reports/summary`, { headers: { 'X-User-Email': 'test@example.com' }});
            // Simulate realistic data
            setPendingTransactions([
                { id: 'tx-1', date: '2026-06-11', vendor: 'Amazon Web Services', amount: 450.00, suggested_gl: '6200 - Hosting', confidence: '99%', reason: 'Rule: AWS -> Hosting' },
                { id: 'tx-2', date: '2026-06-11', vendor: 'Starbucks', amount: 15.40, suggested_gl: '6300 - Meals', confidence: '92%', reason: 'AI Prediction' },
                { id: 'tx-3', date: '2026-06-10', vendor: 'Uber', amount: 42.10, suggested_gl: '6400 - Travel', confidence: '88%', reason: 'AI Prediction' },
                { id: 'tx-4', date: '2026-06-09', vendor: 'Apple', amount: 2499.00, suggested_gl: '1500 - Assets', confidence: '95%', reason: 'Threshold Rule: > $2k' },
            ]);
        } catch (err) {
            console.error('Failed to load pending', err);
        }
    };
    fetchPending();
  }, []);

  const handleApproveAndSync = async (tx: any) => {
    setSyncing(tx.id);
    try {
        const API_BASE_URL = (await import('../config')).default;
        const response = await fetch(`${API_BASE_URL}/sync/qbo/${tx.id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vendor_name: tx.vendor,
                amount: tx.amount,
                gl_code: tx.suggested_gl,
                document_type: 'bill'
            })
        });
        const result = await response.json();
        if (result.status === 'success') {
            setPendingTransactions(prev => prev.filter(item => item.id !== tx.id));
        }
    } catch (err) {
        console.error('Sync failed', err);
    } finally {
        setSyncing(null);
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      <aside className="w-64 bg-white border-r flex flex-col">
        <div className="p-6 border-b">
          <h1 className="text-2xl font-bold text-blue-600">AccountOS</h1>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <Link href="/dashboard" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Dashboard</Link>
          <Link href="/approvals" className="block px-4 py-2 text-blue-600 bg-blue-50 rounded-lg font-medium">Approval Queue</Link>
          <Link href="/transactions" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Transactions</Link>
          <Link href="/settings" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Settings</Link>
        </nav>
      </aside>

      <main className="flex-1 p-8">
        <h1 className="text-3xl font-bold mb-8 text-gray-900">Approval Queue</h1>

        <div className="bg-white border rounded-xl shadow-sm overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="p-4 font-semibold text-gray-600">Date</th>
                <th className="p-4 font-semibold text-gray-600">Vendor</th>
                <th className="p-4 font-semibold text-gray-600">Amount</th>
                <th className="p-4 font-semibold text-gray-600">Suggested GL</th>
                <th className="p-4 font-semibold text-gray-600 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {pendingTransactions.map((tx) => (
                <tr key={tx.id} className="border-b hover:bg-gray-50 transition-colors">
                  <td className="p-4 text-gray-700">{tx.date}</td>
                  <td className="p-4 font-medium text-gray-900">{tx.vendor}</td>
                  <td className="p-4 text-gray-900 font-semibold">${tx.amount}</td>
                  <td className="p-4">
                    <div className="flex flex-col">
                        <span className="text-blue-600 font-medium">{tx.suggested_gl}</span>
                        <span className="text-[10px] text-gray-400">{tx.reason}</span>
                    </div>
                  </td>
                  <td className="p-4 text-right">
                    <button
                        onClick={() => handleApproveAndSync(tx)}
                        disabled={syncing === tx.id}
                        className="bg-green-600 text-white px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-green-700 shadow-sm disabled:bg-gray-300"
                    >
                        {syncing === tx.id ? 'Syncing...' : 'Approve & Sync'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {pendingTransactions.length === 0 && (
            <div className="p-12 text-center text-gray-500">
                <div className="text-4xl mb-4">🎉</div>
                <p className="font-bold text-gray-900">All caught up!</p>
                <p className="text-sm">No transactions pending approval.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
