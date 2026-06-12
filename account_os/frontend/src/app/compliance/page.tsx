'use client';
import { useState, useEffect } from 'react';
import API_BASE_URL from '../config';

export default function CompliancePage() {
    const [logs, setLogs] = useState<any[]>([]);

    useEffect(() => {
        // Mock fetching audit logs
        setLogs([
            { id: 1, action: 'document_ingested', entity: 'INV-100', user: 'AI Agent', time: '10 mins ago' },
            { id: 2, action: 'transaction_coded', entity: 'INV-100', user: 'AI Agent', time: '9 mins ago' },
            { id: 3, action: 'tax_validated', entity: 'INV-100', user: 'Tax Agent', time: '8 mins ago' },
            { id: 4, action: 'sync_success', entity: 'INV-100', user: 'Sync Agent', time: '5 mins ago' },
        ]);
    }, []);

    return (
        <div className="p-8">
            <h1 className="text-3xl font-bold mb-6 text-gray-800">Compliance & Audit Trail</h1>
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-gray-50 border-b border-gray-200 text-gray-500 text-sm font-medium uppercase">
                        <tr>
                            <th className="px-6 py-4">Action</th>
                            <th className="px-6 py-4">Entity</th>
                            <th className="px-6 py-4">Performer</th>
                            <th className="px-6 py-4">Time</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {logs.map(log => (
                            <tr key={log.id} className="hover:bg-gray-50 transition">
                                <td className="px-6 py-4 font-medium text-gray-900">{log.action.replace('_', ' ')}</td>
                                <td className="px-6 py-4 text-gray-600">{log.entity}</td>
                                <td className="px-6 py-4">
                                    <span className="bg-blue-50 text-blue-700 px-2 py-1 rounded-md text-xs font-semibold">{log.user}</span>
                                </td>
                                <td className="px-6 py-4 text-gray-400 text-sm">{log.time}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
