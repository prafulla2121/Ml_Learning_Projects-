export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-6xl font-bold mb-8">AccountOS</h1>
      <p className="text-xl mb-8">AI-Powered Multi-Agent Accounting Platform</p>
      <div className="flex gap-4">
        <a href="/login" className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">Get Started</a>
        <a href="/dashboard" className="border border-blue-600 text-blue-600 px-6 py-2 rounded-lg hover:bg-blue-50">Dashboard</a>
      </div>
    </div>
  );
}
