'use client';
import { useState, useEffect } from 'react';
import API_BASE_URL from '../config';

export default function ReconciliationPage() {
    const [matches, setMatches] = useState(0);

    const runReconciliation = async () => {
        const res = await fetch(`${API_BASE_URL}/reconciliation/run`, {
            method: 'POST',
            headers: { 'X-User-Email': 'test@example.com' }
        });
        const data = await res.json();
        setMatches(data.matches_found);
    };

    return (
        <div className="p-8">
            <h1 className="text-3xl font-bold mb-6">Bank Reconciliation</h1>
            <div className="bg-white p-6 rounded shadow border">
                <p className="mb-4 text-gray-600">Match bank statement entries with your accounting transactions using AI.</p>
                <button
                    onClick={runReconciliation}
                    className="bg-indigo-600 text-white px-6 py-2 rounded font-medium"
                >
                    Run AI Reconciliation
                </button>
                {matches > 0 && (
                    <div className="mt-4 p-3 bg-green-50 text-green-700 rounded border border-green-200">
                        🎉 Success! Found and matched {matches} transactions.
                    </div>
                )}
            </div>
        </div>
    );
}
