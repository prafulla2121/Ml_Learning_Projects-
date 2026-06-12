'use client';
import { useState, useEffect } from 'react';
import API_BASE_URL from '../config';

export default function BillingPage() {
    const [status, setStatus] = useState<any>(null);

    useEffect(() => {
        fetch(`${API_BASE_URL}/billing/status`, {
            headers: { 'X-User-Email': 'test@example.com' }
        })
        .then(res => res.json())
        .then(data => setStatus(data));
    }, []);

    return (
        <div className="p-8">
            <h1 className="text-3xl font-bold mb-6">Billing & Subscription</h1>
            {status && (
                <div className="bg-white p-6 rounded shadow border">
                    <p className="text-lg"><strong>Plan Status:</strong> <span className="text-green-600 uppercase">{status.status}</span></p>
                    <p className="text-lg"><strong>Next Billing:</strong> {status.next_billing_date}</p>
                    <p className="text-lg"><strong>Usage (Docs):</strong> {status.usage_this_month}</p>
                    <button className="mt-4 bg-blue-600 text-white px-4 py-2 rounded">Change Plan</button>
                </div>
            )}
        </div>
    );
}
