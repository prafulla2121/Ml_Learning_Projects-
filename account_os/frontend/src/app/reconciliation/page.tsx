'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function ReconciliationPage() {
  const [reconciliationState, setReconciliationState] = useState({
    matches: [
      { id: 'm1', bank: 'Amazon AMZN.COM', amount: '$124.50', date: '2026-06-10', accounting: 'Amazon.com bill', confidence: '100%' },
      { id: 'm2', bank: 'STK Starbucks', amount: '$12.00', date: '2026-06-11', accounting: 'Starbucks Coffee', confidence: '95%' },
    ],
    unmatched: [
      { id: 'u1', source: 'Bank', desc: 'ATM Withdrawal', amount: '$200.00', date: '2026-06-12' },
      { id: 'u2', source: 'Accounting', desc: 'Office Depot', amount: '$54.20', date: '2026-06-09' },
    ]
  });

  return (
    <div className="flex min-h-screen bg-gray-50">
      <aside className="w-64 bg-white border-r flex flex-col">
        <div className="p-6 border-b">
          <h1 className="text-2xl font-bold text-blue-600">AccountOS</h1>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <Link href="/dashboard" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Dashboard</Link>
          <Link href="/reconciliation" className="block px-4 py-2 text-blue-600 bg-blue-50 rounded-lg font-medium">Reconciliation</Link>
          <Link href="/approvals" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Approval Queue</Link>
          <Link href="/transactions" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Transactions</Link>
          <Link href="/settings" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Settings</Link>
        </nav>
      </aside>

      <main className="flex-1 p-8">
        <h1 className="text-3xl font-bold mb-8 text-gray-900">Bank Reconciliation</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Matches Section */}
            <section className="bg-white border rounded-xl shadow-sm overflow-hidden">
                <div className="p-4 bg-gray-50 border-b flex justify-between items-center">
                    <h2 className="font-semibold text-gray-700">Suggested Matches</h2>
                    <button className="bg-blue-600 text-white px-3 py-1 rounded text-sm font-medium">Approve All</button>
                </div>
                <div className="divide-y">
                    {reconciliationState.matches.map(m => (
                        <div key={m.id} className="p-4 flex flex-col gap-2 hover:bg-blue-50 transition-colors">
                            <div className="flex justify-between items-start">
                                <div>
                                    <p className="text-xs font-bold text-gray-400">BANK STATEMENT</p>
                                    <p className="font-medium">{m.bank}</p>
                                </div>
                                <p className="font-bold text-gray-900">{m.amount}</p>
                            </div>
                            <div className="flex justify-between items-center text-sm border-t pt-2">
                                <div className="text-blue-600 font-medium">↔ {m.accounting}</div>
                                <span className="bg-green-100 text-green-800 text-[10px] px-2 py-0.5 rounded-full font-bold">{m.confidence} Match</span>
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            {/* Unmatched Section */}
            <section className="bg-white border rounded-xl shadow-sm overflow-hidden">
                <div className="p-4 bg-gray-50 border-b">
                    <h2 className="font-semibold text-gray-700">Unmatched Transactions</h2>
                </div>
                <div className="divide-y">
                    {reconciliationState.unmatched.map(u => (
                        <div key={u.id} className="p-4 flex justify-between items-center hover:bg-gray-50">
                            <div>
                                <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold mr-2 ${
                                    u.source === 'Bank' ? 'bg-purple-100 text-purple-800' : 'bg-orange-100 text-orange-800'
                                }`}>{u.source.toUpperCase()}</span>
                                <span className="font-medium text-gray-800">{u.desc}</span>
                                <p className="text-xs text-gray-500">{u.date}</p>
                            </div>
                            <div className="text-right">
                                <p className="font-bold">{u.amount}</p>
                                <button className="text-blue-600 text-xs font-bold hover:underline">Find Match</button>
                            </div>
                        </div>
                    ))}
                </div>
            </section>
        </div>
      </main>
    </div>
  );
}
