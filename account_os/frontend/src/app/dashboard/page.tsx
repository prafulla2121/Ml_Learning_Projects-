export default function DashboardPage() {
  return (
    <div className="flex min-h-screen flex-col p-8">
      <header className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">AccountOS Dashboard</h1>
        <div className="flex gap-4">
          <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">Active Client: ABC Pvt Ltd</span>
        </div>
      </header>

      <main className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="border p-6 rounded-lg shadow-sm bg-white">
          <h2 className="text-xl font-semibold mb-4">Pending Approvals</h2>
          <p className="text-4xl font-bold text-orange-600">12</p>
        </div>
        <div className="border p-6 rounded-lg shadow-sm bg-white">
          <h2 className="text-xl font-semibold mb-4">Total Documents (MTD)</h2>
          <p className="text-4xl font-bold text-blue-600">452</p>
        </div>
        <div className="border p-6 rounded-lg shadow-sm bg-white">
          <h2 className="text-xl font-semibold mb-4">Sync Status</h2>
          <p className="text-4xl font-bold text-green-600">Healthy</p>
        </div>

        <div className="md:col-span-3 border p-6 rounded-lg shadow-sm bg-white">
          <h2 className="text-xl font-semibold mb-4">Recent Transactions</h2>
          <table className="w-full text-left">
            <thead>
              <tr className="border-b">
                <th className="pb-2">Date</th>
                <th className="pb-2">Vendor</th>
                <th className="pb-2">Amount</th>
                <th className="pb-2">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b">
                <td className="py-2">2026-06-09</td>
                <td className="py-2">Amazon</td>
                <td className="py-2">$124.50</td>
                <td className="py-2"><span className="text-green-600">Synced</span></td>
              </tr>
              <tr className="border-b">
                <td className="py-2">2026-06-08</td>
                <td className="py-2">DigitalOcean</td>
                <td className="py-2">$40.00</td>
                <td className="py-2"><span className="text-orange-600">Pending Review</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
