export default function SettingsPage() {
  return (
    <div className="flex min-h-screen flex-col p-8">
      <h1 className="text-3xl font-bold mb-8">Settings</h1>

      <div className="max-w-2xl space-y-8">
        <section className="border p-6 rounded-lg bg-white shadow-sm">
          <h2 className="text-xl font-semibold mb-4">Accounting Platform</h2>
          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between p-3 border rounded">
              <span>QuickBooks Online</span>
              <button className="text-blue-600 font-medium">Configure</button>
            </div>
            <div className="flex items-center justify-between p-3 border rounded">
              <span>Xero</span>
              <button className="text-blue-600 font-medium">Connect</button>
            </div>
          </div>
        </section>

        <section className="border p-6 rounded-lg bg-white shadow-sm">
          <h2 className="text-xl font-semibold mb-4">GL Mapping Rules</h2>
          <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
            Add New Rule
          </button>
        </section>

        <section className="border p-6 rounded-lg bg-white shadow-sm">
          <h2 className="text-xl font-semibold mb-4">Approval Workflows</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span>Threshold: &gt; $5,000</span>
              <span className="text-gray-600">Approver: Finance Manager</span>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
