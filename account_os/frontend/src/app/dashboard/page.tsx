'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function DashboardPage() {
  const [uploading, setUploading] = useState(false);
  const [activeJobs, setActiveJobs] = useState<any[]>([]);

  const handleFileUpload = async (e: any) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    try {
        const API_BASE_URL = (await import('../config')).default;
        const response = await fetch(`${API_BASE_URL}/documents/upload`, {
            method: 'POST',
            body: formData,
        });
        const data = await response.json();
        setActiveJobs(prev => [...prev, ...data.documents]);
    } catch (err) {
        console.error('Upload failed', err);
    } finally {
        setUploading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
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
      </aside>

      <main className="flex-1 p-8">
        <header className="flex justify-between items-center mb-8">
          <h2 className="text-3xl font-bold">Dashboard</h2>
          <div className="flex items-center gap-4">
              <label className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 cursor-pointer">
                  {uploading ? 'Uploading...' : '+ Upload Documents'}
                  <input type="file" multiple className="hidden" onChange={handleFileUpload} disabled={uploading} />
              </label>
          </div>
        </header>

        {activeJobs.length > 0 && (
            <section className="mb-8 bg-blue-50 border border-blue-200 rounded-xl p-6">
                <h3 className="text-blue-800 font-bold mb-4">Current Processing</h3>
                <div className="space-y-3">
                    {activeJobs.map(job => (
                        <div key={job.file_id} className="bg-white p-3 rounded-lg flex justify-between items-center shadow-sm border border-blue-100">
                            <div className="flex items-center gap-3">
                                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                                <span className="text-sm font-medium">{job.filename}</span>
                            </div>
                            <span className="text-xs text-blue-600 font-bold">AI ANALYZING...</span>
                        </div>
                    ))}
                </div>
            </section>
        )}

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
                    <div className="p-4 bg-gray-50 border-b font-bold text-gray-700">✨ AI Insights</div>
                    <div className="p-4 space-y-4">
                        <div className="p-3 rounded-lg border-l-4 bg-red-50 border-red-500">
                            <p className="font-bold text-sm">Duplicate Detected</p>
                            <p className="text-xs mt-1">Two identical bills from Amazon found.</p>
                        </div>
                    </div>
                </section>
            </div>
        </div>
      </main>
    </div>
  );
}
