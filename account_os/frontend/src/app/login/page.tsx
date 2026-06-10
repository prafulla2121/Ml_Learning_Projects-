export default function LoginPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex border p-8 rounded-lg shadow-md bg-white">
        <h1 className="text-4xl font-bold mb-8">AccountOS Login</h1>
        <form className="flex flex-col gap-4 w-full max-w-sm">
          <input
            type="email"
            placeholder="Email"
            className="p-2 border rounded"
          />
          <input
            type="password"
            placeholder="Password"
            className="p-2 border rounded"
          />
          <button
            type="button"
            className="bg-blue-600 text-white p-2 rounded hover:bg-blue-700"
          >
            Sign In
          </button>
        </form>
      </div>
    </div>
  );
}
