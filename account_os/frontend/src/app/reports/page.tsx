'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function ReportsPage() {
  const [reportData, setReportData] = useState({
    summary: {
        income: '$45,200.00',
        expenses: '$32,150.00',
        profit: '$13,050.00'
    },
    categories: [
        { name: 'Office Supplies', amount: '$4,500', percent: 14 },
        { name: 'Rent', amount: '$12,000', percent: 37 },
        { name: 'Payroll', amount: '$15,000', percent: 46 },
        { name: 'Marketing', amount: '$650', percent: 3 },
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
          <Link href="/reconciliation" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Reconciliation</Link>
          <Link href="/approvals" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Approval Queue</Link>
          <Link href="/transactions" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Transactions</Link>
          <Link href="/reports" className="block px-4 py-2 text-blue-600 bg-blue-50 rounded-lg font-medium">Reports</Link>
          <Link href="/settings" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Settings</Link>
        </nav>
      </aside>

      <main className="flex-1 p-8">
        <h1 className="text-3xl font-bold mb-8 text-gray-900">Financial Reports</h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white p-6 rounded-xl border shadow-sm">
                <h3 className="text-sm font-medium text-gray-500 mb-2">Total Income</h3>
                <p className="text-2xl font-bold text-green-600">{reportData.summary.income}</p>
            </div>
            <div className="bg-white p-6 rounded-xl border shadow-sm">
                <h3 className="text-sm font-medium text-gray-500 mb-2">Total Expenses</h3>
                <p className="text-2xl font-bold text-red-600">{reportData.summary.expenses}</p>
            </div>
            <div className="bg-white p-6 rounded-xl border shadow-sm">
                <h3 className="text-sm font-medium text-gray-500 mb-2">Net Profit</h3>
                <p className="text-2xl font-bold text-blue-600">{reportData.summary.profit}</p>
            </div>
        </div>

        <div className="bg-white border rounded-xl shadow-sm p-8">
            <h2 className="text-xl font-semibold mb-6">Expense Breakdown</h2>
            <div className="space-y-6">
                {reportData.categories.map(cat => (
                    <div key={cat.name}>
                        <div className="flex justify-between items-center mb-2">
                            <span className="font-medium text-gray-700">{cat.name}</span>
                            <span className="text-gray-900 font-bold">{cat.amount}</span>
                        </div>
                        <div className="w-full bg-gray-100 rounded-full h-2">
                            <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${cat.percent}%` }}></div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
      </main>
    </div>
  );
}
