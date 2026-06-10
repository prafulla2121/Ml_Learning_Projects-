'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState([
    { id: '1', date: '2026-06-10', vendor: 'Amazon', amount: '$124.50', gl_code: '6200', status: 'Synced', platform: 'QBO' },
    { id: '2', date: '2026-06-09', vendor: 'DigitalOcean', amount: '$40.00', gl_code: '6100', status: 'Synced', platform: 'QBO' },
    { id: '3', date: '2026-06-08', vendor: 'Apple', amount: '$1,299.00', gl_code: '1500', status: 'Pending Review', platform: 'Xero' },
    { id: '4', date: '2026-06-07', vendor: 'Starbucks', amount: '$5.50', gl_code: '7100', status: 'Rejected', platform: 'QBO' },
    { id: '5', date: '2026-06-06', vendor: 'Uber', amount: '$25.00', gl_code: '6300', status: 'Synced', platform: 'QBO' },
    { id: '6', date: '2026-06-05', vendor: 'Slack', amount: '$240.00', gl_code: '6100', status: 'Synced', platform: 'QBO' },
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
          <Link href="/approvals" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Approval Queue</Link>
          <Link href="/transactions" className="block px-4 py-2 text-blue-600 bg-blue-50 rounded-lg font-medium">Transactions</Link>
          <Link href="/settings" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Settings</Link>
        </nav>
      </aside>

      <main className="flex-1 p-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Transaction History</h1>
          <div className="flex gap-4">
            <input type="text" placeholder="Search vendors..." className="border p-2 rounded-lg w-64 shadow-sm focus:ring-2 focus:ring-blue-500 outline-none" />
            <select className="border p-2 rounded-lg shadow-sm">
              <option>All Platforms</option>
              <option>QuickBooks Online</option>
              <option>Xero</option>
            </select>
          </div>
        </div>

        <div className="bg-white border rounded-xl shadow-sm overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="p-4 font-semibold text-gray-600">Date</th>
                <th className="p-4 font-semibold text-gray-600">Vendor</th>
                <th className="p-4 font-semibold text-gray-600">Amount</th>
                <th className="p-4 font-semibold text-gray-600">GL Code</th>
                <th className="p-4 font-semibold text-gray-600">Status</th>
                <th className="p-4 font-semibold text-gray-600">Platform</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx) => (
                <tr key={tx.id} className="border-b hover:bg-gray-50 transition-colors">
                  <td className="p-4 text-gray-700">{tx.date}</td>
                  <td className="p-4 font-medium text-gray-900">{tx.vendor}</td>
                  <td className="p-4 text-gray-900 font-semibold">{tx.amount}</td>
                  <td className="p-4 text-gray-600 font-mono">{tx.gl_code}</td>
                  <td className="p-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                      tx.status === 'Synced' ? 'bg-green-100 text-green-800' :
                      tx.status === 'Pending Review' ? 'bg-orange-100 text-orange-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {tx.status}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className="text-xs font-bold text-gray-400 bg-gray-100 px-2 py-0.5 rounded">{tx.platform}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="p-4 bg-gray-50 border-t flex justify-between items-center text-sm text-gray-500">
            <span>Showing {transactions.length} transactions</span>
            <div className="flex gap-2">
              <button className="px-3 py-1 border rounded bg-white disabled:opacity-50">Previous</button>
              <button className="px-3 py-1 border rounded bg-white">Next</button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
