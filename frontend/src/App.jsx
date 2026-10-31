export default function App() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      <header className="border-b border-slate-200 bg-white">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold text-xl shadow-sm">
              ISL
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-900 leading-tight">
                Indian Sign Language Alphabet Recognition
              </h1>
              <p className="text-xs text-slate-500">
                Voice Conversion System &bull; B.Tech Academic Project
              </p>
            </div>
          </div>
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
            Phase 1: Environment Ready
          </span>
        </div>
      </header>

      <main className="flex-1 max-w-6xl mx-auto px-6 py-12 w-full">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8">
          <div className="max-w-2xl">
            <span className="text-xs font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-3 py-1 rounded-full">
              System Foundation Verified
            </span>
            <h2 className="mt-4 text-2xl font-extrabold text-slate-900 tracking-tight">
              React + Vite + Tailwind CSS Development Environment
            </h2>
            <p className="mt-3 text-slate-600 leading-relaxed text-sm">
              The project structure, reference architecture (PDR &amp; TDR), and team knowledge hub are properly configured. The application is ready for Phase 2 (Dataset Audit Gate) and subsequent ML pipeline development.
            </p>

            <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Target Scope</div>
                <div className="mt-1 text-base font-bold text-slate-800">ISL A–Z Fingerspelling</div>
              </div>
              <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Inference Core</div>
                <div className="mt-1 text-base font-bold text-slate-800">TensorFlow CNN + OpenCV</div>
              </div>
              <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Voice Conversion</div>
                <div className="mt-1 text-base font-bold text-slate-800">Web SpeechSynthesis</div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <footer className="border-t border-slate-200 py-6 text-center text-xs text-slate-500 bg-white">
        AI-Based Indian Sign Language Alphabet Recognition and Voice Conversion System &bull; B.Tech AI/ML Project
      </footer>
    </div>
  )
}
