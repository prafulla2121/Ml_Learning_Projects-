'use client';

import Link from 'next/link';

export default function DashboardPage() {
  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r flex flex-col">
        <div className="p-6 border-b">
          <h1 className="text-2xl font-bold text-blue-600">AccountOS</h1>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <Link href="/dashboard" className="block px-4 py-2 text-blue-600 bg-blue-50 rounded-lg font-medium">Dashboard</Link>
          <Link href="/approvals" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Approval Queue</Link>
          <Link href="/transactions" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Transactions</Link>
          <Link href="/settings" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Settings</Link>
        </nav>
        <div className="p-4 border-t">
          <div className="flex items-center gap-3 px-4 py-2">
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold">A</div>
            <div className="text-sm">
              <p className="font-medium">ABC Pvt Ltd</p>
              <p className="text-gray-500">Plan: Pro</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8">
        <header className="flex justify-between items-center mb-8">
          <h2 className="text-3xl font-bold">Overview</h2>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700">+ Upload Document</button>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white border p-6 rounded-xl shadow-sm">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Pending Approvals</h3>
            <p className="text-3xl font-bold text-orange-600">12</p>
          </div>
          <div className="bg-white border p-6 rounded-xl shadow-sm">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Total MTD</h3>
            <p className="text-3xl font-bold text-blue-600">452</p>
          </div>
          <div className="bg-white border p-6 rounded-xl shadow-sm">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Active Platforms</h3>
            <p className="text-3xl font-bold">1/3</p>
          </div>
          <div className="bg-white border p-6 rounded-xl shadow-sm">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Health Score</h3>
            <p className="text-3xl font-bold text-green-600">98%</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white border p-6 rounded-xl shadow-sm">
            <h3 className="text-lg font-semibold mb-4">Sync Activity</h3>
            <div className="h-64 flex items-end justify-between gap-2 px-4 pb-4">
              {[40, 70, 45, 90, 65, 80, 50].map((h, i) => (
                <div key={i} className="w-full bg-blue-100 rounded-t" style={{height: `${h}%`}}></div>
              ))}
            </div>
          </div>
          <div className="bg-white border p-6 rounded-xl shadow-sm">
            <h3 className="text-lg font-semibold mb-4">Recent Transactions</h3>
            <div className="space-y-4">
              {[
                { vendor: 'Amazon', amount: '$124.50', status: 'Synced' },
                { vendor: 'DigitalOcean', amount: '$40.00', status: 'Synced' },
                { vendor: 'Apple', amount: '$1,299.00', status: 'Pending' },
              ].map((tx, i) => (
                <div key={i} className="flex justify-between items-center p-3 border rounded-lg">
                  <div>
                    <p className="font-medium">{tx.vendor}</p>
                    <p className="text-xs text-gray-500">2 hours ago</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold">{tx.amount}</p>
                    <p className={`text-xs ${tx.status === 'Synced' ? 'text-green-600' : 'text-orange-600'}`}>{tx.status}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
