import { Link } from "react-router-dom";

export function LoginPage() {
  const leaderboardData = [
    { username: "w0rdmaster", points: 1238, rank: 1 },
    { username: "deducto42", points: 1239, rank: 2 },
    { username: "guesserino", points: 1261, rank: 3 },
    { username: "scrabbly", points: 1260, rank: 4 },
    { username: "lingolegend", points: 1250, rank: 5 },
    { username: "puzzler975", points: 1128, rank: 6 },
    { username: "vocabvulture", points: 1133, rank: 7 },
    { username: "cryptospell", points: 1155, rank: 8 },
    { username: "lexiconking", points: 1850, rank: 9 },
    { username: "anagramadept", points: 850, rank: 10 },
  ];

  return (
    <div className="min-h-screen flex items-center justify-center px-8 py-12 dark">
      {/* Dark gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#0a0a0a] via-[#1a1a1a] to-[#0f0f0f]" />
      
      {/* Main container */}
      <div className="relative z-10 w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-16">
        
        {/* Left Column - Authentication Panel */}
        <div className="flex flex-col justify-center space-y-8">
          {/* Title */}
          <div className="space-y-2">
            <h1 className="text-5xl font-bold tracking-tight text-white">
              HARDLE
            </h1>
            <p className="text-gray-500">
              Server-Authoritative Word Deduction Game
            </p>
          </div>

          {/* Log In Section */}
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold text-white">
              Log In
            </h2>

            {/* Form */}
            <form className="space-y-4">
              {/* Email Input */}
              <div className="space-y-2">
                <label htmlFor="email" className="block text-sm text-gray-400">
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  placeholder="Email"
                  className="w-full px-4 py-3 bg-[#1a1a1a] border border-gray-800 rounded-lg text-white placeholder:text-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-700 focus:border-transparent transition-all"
                />
              </div>

              {/* Password Input */}
              <div className="space-y-2">
                <label htmlFor="password" className="block text-sm text-gray-400">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  placeholder="Password"
                  className="w-full px-4 py-3 bg-[#1a1a1a] border border-gray-800 rounded-lg text-white placeholder:text-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-700 focus:border-transparent transition-all"
                />
              </div>

              {/* Log In Button */}
              <button
                type="submit"
                className="w-full px-6 py-3 bg-[#d4a933] hover:bg-[#e0b840] text-black font-semibold rounded-lg transition-colors duration-200"
              >
                Log In
              </button>
            </form>

            {/* Sign Up Link */}
            <p className="text-sm text-gray-500 text-center">
              Don't have an account?{" "}
              <Link to="/" className="text-[#d4a933] hover:text-[#e0b840] transition-colors">
                Sign up here
              </Link>
            </p>
          </div>
        </div>

        {/* Right Column - Leaderboard Panel */}
        <div className="flex flex-col justify-center">
          <div className="bg-[#161616] border border-gray-800 rounded-2xl p-6 space-y-6">
            <h2 className="text-2xl font-semibold text-white">
              Leaderboard
            </h2>

            {/* Leaderboard Table */}
            <div className="space-y-1">
              {/* Header */}
              <div className="grid grid-cols-2 pb-3 border-b border-gray-800">
                <div className="text-sm font-medium text-gray-400">User</div>
                <div className="text-sm font-medium text-gray-400 text-right">Points</div>
              </div>

              {/* Leaderboard Entries */}
              <div className="space-y-0.5">
                {leaderboardData.map((entry, index) => (
                  <div
                    key={index}
                    className={`grid grid-cols-2 py-3 border-b border-gray-800/50 last:border-0 ${
                      index < 3 ? "text-white" : "text-gray-400"
                    }`}
                  >
                    <div className={`${index < 3 ? "text-[#d4a933]" : ""}`}>
                      {entry.username}
                    </div>
                    <div className={`text-right ${index < 3 ? "font-medium" : ""}`}>
                      {entry.points}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
