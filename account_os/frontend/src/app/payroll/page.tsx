'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function PayrollPage() {
  const [payrollEntries, setPayrollEntries] = useState([
    { id: 'p1', date: '2026-05-31', status: 'Synced', amount: '$10,800.00', employees: 5 },
    { id: 'p2', date: '2026-06-30', status: 'Draft', amount: '$11,200.00', employees: 5 },
  ]);

  return (
    <div className="flex min-h-screen bg-gray-50">
      <aside className="w-64 bg-white border-r flex flex-col">
        <div className="p-6 border-b">
          <h1 className="text-2xl font-bold text-blue-600">AccountOS</h1>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <Link href="/dashboard" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Dashboard</Link>
          <Link href="/payroll" className="block px-4 py-2 text-blue-600 bg-blue-50 rounded-lg font-medium">Payroll</Link>
          <Link href="/invoicing" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Invoicing (AR)</Link>
          <Link href="/settings" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Settings</Link>
        </nav>
      </aside>

      <main className="flex-1 p-8">
        <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Payroll Automation</h1>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium">Upload Payroll File</button>
        </div>

        <div className="bg-white border rounded-xl shadow-sm overflow-hidden">
            <table className="w-full text-left">
                <thead className="bg-gray-50 border-b">
                    <tr>
                        <th className="p-4 font-semibold text-gray-600">Period End</th>
                        <th className="p-4 font-semibold text-gray-600">Employees</th>
                        <th className="p-4 font-semibold text-gray-600">Total JE Amount</th>
                        <th className="p-4 font-semibold text-gray-600">Status</th>
                        <th className="p-4 font-semibold text-gray-600 text-right">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {payrollEntries.map(p => (
                        <tr key={p.id} className="border-b hover:bg-gray-50">
                            <td className="p-4 font-medium">{p.date}</td>
                            <td className="p-4">{p.employees}</td>
                            <td className="p-4 font-bold">{p.amount}</td>
                            <td className="p-4">
                                <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                                    p.status === 'Synced' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                                }`}>{p.status}</span>
                            </td>
                            <td className="p-4 text-right">
                                <button className="text-blue-600 font-bold text-sm hover:underline">View Journal Entry</button>
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
