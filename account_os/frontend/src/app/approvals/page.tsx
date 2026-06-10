'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function ApprovalQueuePage() {
  const [pendingTransactions, setPendingTransactions] = useState([
    {
      id: '1',
      date: '2026-06-10',
      vendor: 'Amazon',
      amount: '$124.50',
      suggested_gl: '6200 - Office Supplies',
      confidence: '98%',
      reason: 'Rule: Amazon -> 6200'
    },
    {
      id: '2',
      date: '2026-06-11',
      vendor: 'Starbucks',
      amount: '$12.00',
      suggested_gl: '7100 - Staff Welfare',
      confidence: '85%',
      reason: 'AI Suggestion'
    },
    {
        id: '3',
        date: '2026-06-12',
        vendor: 'Microsoft',
        amount: '$299.99',
        suggested_gl: '6100 - Software Subscription',
        confidence: '92%',
        reason: 'AI Suggestion'
      }
  ]);

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar (Shared) */}
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
                <th className="p-4 font-semibold text-gray-600">Confidence</th>
                <th className="p-4 font-semibold text-gray-600 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {pendingTransactions.map((tx) => (
                <tr key={tx.id} className="border-b hover:bg-gray-50 transition-colors">
                  <td className="p-4 text-gray-700">{tx.date}</td>
                  <td className="p-4 font-medium text-gray-900">{tx.vendor}</td>
                  <td className="p-4 text-gray-900 font-semibold">{tx.amount}</td>
                  <td className="p-4">
                    <div className="flex flex-col">
                        <span className="text-blue-600 hover:underline cursor-pointer font-medium">{tx.suggested_gl}</span>
                        <span className="text-[10px] text-gray-400">{tx.reason}</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                      parseInt(tx.confidence) > 90 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {tx.confidence}
                    </span>
                  </td>
                  <td className="p-4 text-right">
                    <div className="flex gap-2 justify-end">
                      <button className="bg-green-600 text-white px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-green-700 shadow-sm transition-colors">Approve</button>
                      <button className="border border-gray-300 px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-gray-100 transition-colors">Edit</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {pendingTransactions.length === 0 && (
            <div className="p-8 text-center text-gray-500">
                All caught up! No transactions pending approval.
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
