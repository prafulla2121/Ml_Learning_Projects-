'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function InvoicingPage() {
  const [invoices, setInvoices] = useState([
    { id: 'inv1', customer: 'Global Tech', amount: '$5,000.00', due: '2026-06-01', status: 'Overdue' },
    { id: 'inv2', customer: 'SoftCorp', amount: '$1,200.00', due: '2026-06-15', status: 'Sent' },
    { id: 'inv3', customer: 'MainStreet Inc', amount: '$450.00', due: '2026-06-20', status: 'Draft' },
  ]);

  return (
    <div className="flex min-h-screen bg-gray-50">
      <aside className="w-64 bg-white border-r flex flex-col">
        <div className="p-6 border-b">
          <h1 className="text-2xl font-bold text-blue-600">AccountOS</h1>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <Link href="/dashboard" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Dashboard</Link>
          <Link href="/invoicing" className="block px-4 py-2 text-blue-600 bg-blue-50 rounded-lg font-medium">Invoicing (AR)</Link>
          <Link href="/approvals" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Approval Queue</Link>
          <Link href="/transactions" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Transactions</Link>
          <Link href="/settings" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Settings</Link>
        </nav>
      </aside>

      <main className="flex-1 p-8">
        <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Accounts Receivable</h1>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium">+ New Invoice</button>
        </div>

        <div className="bg-white border rounded-xl shadow-sm overflow-hidden">
            <table className="w-full text-left">
                <thead className="bg-gray-50 border-b">
                    <tr>
                        <th className="p-4 font-semibold text-gray-600">Customer</th>
                        <th className="p-4 font-semibold text-gray-600">Amount</th>
                        <th className="p-4 font-semibold text-gray-600">Due Date</th>
                        <th className="p-4 font-semibold text-gray-600">Status</th>
                        <th className="p-4 font-semibold text-gray-600 text-right">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {invoices.map(inv => (
                        <tr key={inv.id} className="border-b hover:bg-gray-50">
                            <td className="p-4 font-medium">{inv.customer}</td>
                            <td className="p-4 font-bold">{inv.amount}</td>
                            <td className="p-4 text-gray-600">{inv.due}</td>
                            <td className="p-4">
                                <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                                    inv.status === 'Overdue' ? 'bg-red-100 text-red-800' :
                                    inv.status === 'Sent' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                                }`}>{inv.status}</span>
                            </td>
                            <td className="p-4 text-right">
                                <button className="text-blue-600 font-bold text-sm hover:underline">Send Reminder</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
      </main>
    </div>
  );
}
