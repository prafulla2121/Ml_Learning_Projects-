'use client';
import { useState } from 'react';

export default function InsightsPage() {
    const [insights] = useState([
        { title: 'Duplicate Bill Detected', desc: 'Two identical bills from Amazon found in entity ABC.', severity: 'high' },
        { title: 'Spending Spike', desc: 'Office supplies spending is 40% higher than last month.', severity: 'medium' },
        { title: 'New Vendor', desc: 'First time transaction with DigitalOcean recorded.', severity: 'low' },
    ]);

    return (
        <div className="p-8">
            <h1 className="text-3xl font-bold mb-6 text-gray-800 font-hindi">AI Insights</h1>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-indigo-600 text-white p-6 rounded-xl shadow-lg">
                    <p className="opacity-80 text-sm">Efficiency Score</p>
                    <h2 className="text-4xl font-bold mt-1">94%</h2>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <p className="text-gray-500 text-sm font-medium">Potential Savings</p>
                    <h2 className="text-4xl font-bold mt-1 text-green-600">$1,240</h2>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <p className="text-gray-500 text-sm font-medium">Anomalies Detected</p>
                    <h2 className="text-4xl font-bold mt-1 text-red-500">2</h2>
                </div>
            </div>

            <div className="space-y-4">
                {insights.map((ins, i) => (
                    <div key={i} className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex items-start gap-4">
                        <div className={`w-3 h-3 rounded-full mt-1.5 ${ins.severity === 'high' ? 'bg-red-500' : ins.severity === 'medium' ? 'bg-amber-500' : 'bg-blue-500'}`} />
                        <div>
                            <h3 className="font-bold text-gray-900">{ins.title}</h3>
                            <p className="text-gray-600 text-sm mt-1">{ins.desc}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
