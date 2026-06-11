'use client';

import Link from 'next/link';

export default function DashboardPage() {
  const insights = [
    { id: 1, type: 'anomaly', title: 'Duplicate Detected', desc: 'Two identical bills from Amazon found.', severity: 'high' },
    { id: 2, type: 'insight', title: 'Cash Flow Tip', desc: 'Switching to annual billing for Slack could save $400/year.', severity: 'low' },
  ];

  return (
    <div className="flex min-h-screen bg-gray-50">
      <aside className="w-64 bg-white border-r flex flex-col">
        <div className="p-6 border-b">
          <h1 className="text-2xl font-bold text-blue-600">AccountOS</h1>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <Link href="/dashboard" className="block px-4 py-2 text-blue-600 bg-blue-50 rounded-lg font-medium">Dashboard</Link>
          <Link href="/reconciliation" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Reconciliation</Link>
          <Link href="/invoicing" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Invoicing (AR)</Link>
          <Link href="/approvals" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Approval Queue</Link>
          <Link href="/transactions" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Transactions</Link>
          <Link href="/reports" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Reports</Link>
          <Link href="/settings" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Settings</Link>
        </nav>
      </aside>

      <main className="flex-1 p-8">
        <header className="flex justify-between items-center mb-8">
          <h2 className="text-3xl font-bold">Dashboard</h2>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700">+ Upload Document</button>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-8">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-white border p-6 rounded-xl shadow-sm">
                        <h3 className="text-sm font-medium text-gray-500 mb-2">Pending Approvals</h3>
                        <p className="text-3xl font-bold text-orange-600">12</p>
                    </div>
                    <div className="bg-white border p-6 rounded-xl shadow-sm">
                        <h3 className="text-sm font-medium text-gray-500 mb-2">Total MTD</h3>
                        <p className="text-3xl font-bold text-blue-600">452</p>
                    </div>
                    <div className="bg-white border p-6 rounded-xl shadow-sm">
                        <h3 className="text-sm font-medium text-gray-500 mb-2">Health Score</h3>
                        <p className="text-3xl font-bold text-green-600">98%</p>
                    </div>
                </div>

                <div className="bg-white border p-6 rounded-xl shadow-sm">
                    <h3 className="text-lg font-semibold mb-4">Sync Activity</h3>
                    <div className="h-48 flex items-end justify-between gap-2">
                        {[40, 70, 45, 90, 65, 80, 50].map((h, i) => (
                            <div key={i} className="w-full bg-blue-100 rounded-t" style={{height: `${h}%`}}></div>
                        ))}
                    </div>
                </div>
            </div>

            <div className="space-y-8">
                <section className="bg-white border rounded-xl shadow-sm overflow-hidden">
                    <div className="p-4 bg-gray-50 border-b">
                        <h3 className="font-bold text-gray-700 flex items-center gap-2">
                            <span>✨ AI Insights</span>
                            <span className="bg-blue-600 text-white text-[10px] px-1.5 py-0.5 rounded-full">NEW</span>
                        </h3>
                    </div>
                    <div className="p-4 space-y-4">
                        {insights.map(ins => (
                            <div key={ins.id} className={`p-3 rounded-lg border-l-4 ${
                                ins.type === 'anomaly' ? 'bg-red-50 border-red-500' : 'bg-blue-50 border-blue-500'
                            }`}>
                                <p className="font-bold text-sm text-gray-900">{ins.title}</p>
                                <p className="text-xs text-gray-600 mt-1">{ins.desc}</p>
                            </div>
                        ))}
                    </div>
                </section>
            </div>
        </div>
      </main>
    </div>
  );
}
