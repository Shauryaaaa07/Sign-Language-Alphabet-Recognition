import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, AlertTriangle, ArrowRight } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import Modal from '../components/Modal';

/**
 * Detailed gesture metadata for educational guidance based on verified test results
 */
const ALPHABET_METADATA = {
  A: { desc: 'Closed fist with the thumb resting alongside the curled fingers, facing forward.', difficulty: 'Easy', acc: '88.9%' },
  B: { desc: 'Open palm with four fingers straight up and thumb folded across the palm.', difficulty: 'Easy', acc: '93.0%' },
  C: { desc: 'Curved fingers and thumb forming a visible "C" cup shape facing sideways.', difficulty: 'Easy', acc: '88.7%' },
  D: { desc: 'Index finger pointing straight up, while other fingers touch thumb tip.', difficulty: 'Easy', acc: '100%' },
  E: { desc: 'All fingertips curled inward touching the edge of the folded thumb.', difficulty: 'Medium', acc: '73.4%' },
  F: { desc: 'Thumb and index finger touching to form a circle; remaining three fingers upright.', difficulty: 'Easy', acc: '89.5%' },
  G: { desc: 'Index finger pointing horizontally forward with thumb extended parallel.', difficulty: 'Easy', acc: '97.0%' },
  H: { desc: 'Index and middle fingers extended together horizontally forward.', difficulty: 'Easy', acc: '100%' },
  I: { desc: 'Closed fist with only the pinky finger extended straight upward.', difficulty: 'Medium', acc: '69.4%' },
  J: { desc: 'Pinky finger extended with static keyframe posture (traces downward hook in natural ISL motion).', difficulty: 'Dynamic', acc: '98.2%', isDynamic: true },
  K: { desc: 'Index finger straight up, middle finger angled forward, thumb resting between them.', difficulty: 'Easy', acc: '99.5%' },
  L: { desc: 'Index finger vertical and thumb horizontal forming an exact "L" angle.', difficulty: 'Easy', acc: '100%' },
  M: { desc: 'Thumb tucked under three folded fingers (index, middle, ring).', difficulty: 'Medium', acc: '95.7%' },
  N: { desc: 'Thumb tucked under two folded fingers (index and middle).', difficulty: 'Medium', acc: '86.7%' },
  O: { desc: 'All fingertips touching the thumb tip to form an "O" shape.', difficulty: 'Easy', acc: '94.5%' },
  P: { desc: 'Downwards-angled "K" sign with index finger forward and middle finger pointing down.', difficulty: 'Medium', acc: '97.3%' },
  Q: { desc: 'Downwards-angled "G" hand with index and thumb pointing downward.', difficulty: 'Medium', acc: '78.1%' },
  R: { desc: 'Index and middle fingers crossed over each other facing upward.', difficulty: 'Easy', acc: '100%' },
  S: { desc: 'Compact clenched fist with thumb wrapped across the front of the curled fingers.', difficulty: 'Hard', acc: '40.0%', isDifficult: true },
  T: { desc: 'Thumb inserted between index and middle fingers of a closed fist.', difficulty: 'Medium', acc: '88.8%' },
  U: { desc: 'Index and middle fingers held straight and tightly together upward.', difficulty: 'Easy', acc: '87.9%' },
  V: { desc: 'Index and middle fingers spread apart forming a "V" peace sign.', difficulty: 'Easy', acc: '83.2%' },
  W: { desc: 'Three fingers (index, middle, ring) held upright and spread apart.', difficulty: 'Hard', acc: '0.0%', isDifficult: true },
  X: { desc: 'Index finger hooked or bent at the knuckle like a question mark.', difficulty: 'Medium', acc: '77.5%' },
  Y: { desc: 'Thumb and pinky extended wide outward with middle three fingers curled in.', difficulty: 'Easy', acc: '88.9%' },
  Z: { desc: 'Perpendicular palm static keyframe posture (traces "Z" zigzag in natural ISL motion).', difficulty: 'Dynamic', acc: '66.7%', isDynamic: true },
};

/**
 * Learn Component
 * Educational lexicon for all 26 Indian Sign Language alphabet classes
 * presented in Modern Indigo AI (Linear & Cursor style).
 */
export default function Learn({ onSelectLetterForPractice }) {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [activeModalLetter, setActiveModalLetter] = useState(null);

  const vowels = ['A', 'E', 'I', 'O', 'U'];
  const alphabetList = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');

  const filteredLetters = alphabetList.filter((letter) => {
    const meta = ALPHABET_METADATA[letter] || {};
    const matchesSearch =
      letter.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (meta.desc && meta.desc.toLowerCase().includes(searchQuery.toLowerCase()));

    if (!matchesSearch) return false;

    if (filterType === 'vowels') return vowels.includes(letter);
    if (filterType === 'consonants') return !vowels.includes(letter);
    if (filterType === 'high_acc') return parseFloat(meta.acc) >= 95.0;
    if (filterType === 'dynamic') return Boolean(meta.isDynamic);
    return true;
  });

  const handlePracticeInStudio = (letter) => {
    if (onSelectLetterForPractice) {
      onSelectLetterForPractice(letter);
    }
    setActiveModalLetter(null);
    navigate('/studio');
  };

  const selectedMeta = activeModalLetter ? ALPHABET_METADATA[activeModalLetter] : null;

  return (
    <div className="space-y-6 py-4">
      <PageHeader
        badge="Lexicon Library"
        title="Indian Sign Language Alphabet (A–Z)"
        subtitle="Explore all 26 fingerspelling hand pose references, biomechanical positioning instructions, and independently audited classification metrics."
      />

      {/* Search and Filters Bar */}
      <div className="card-linear p-3.5 sm:p-4 flex flex-col md:flex-row items-center justify-between gap-3 shadow-md">
        {/* Search Input */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search letters (e.g. A, B, C)..."
            className="w-full bg-slate-50 dark:bg-[#161926] border border-slate-200/80 dark:border-white/[0.08] rounded-xl pl-9 pr-3.5 py-2 text-xs sm:text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-hidden font-mono focus:border-indigo-500 transition-colors"
          />
        </div>

        {/* Filter Buttons */}
        <div className="flex flex-wrap items-center gap-1.5 w-full md:w-auto">
          {[
            { id: 'all', label: 'All Letters (26)' },
            { id: 'vowels', label: 'Vowels (5)' },
            { id: 'consonants', label: 'Consonants (21)' },
            { id: 'high_acc', label: 'High Acc (>95%)' },
            { id: 'dynamic', label: 'Dynamic (J & Z)' },
          ].map(({ id, label }) => (
            <button
              key={id}
              type="button"
              onClick={() => setFilterType(id)}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold font-mono transition-all ${
                filterType === id
                  ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-md shadow-indigo-500/25'
                  : 'bg-slate-100 dark:bg-white/[0.04] text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/60 dark:hover:bg-white/[0.08]'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Movement Limitation Notice */}
      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs sm:text-sm text-amber-700 dark:text-amber-300 flex items-start space-x-3 shadow-xs">
        <AlertTriangle className="w-4 h-4 shrink-0 text-amber-500 mt-0.5" />
        <div className="space-y-0.5">
          <p className="font-bold">Dynamic Signs Boundary Disclosure (J &amp; Z)</p>
          <p className="text-xs leading-relaxed">
            In conversational Indian Sign Language, letters <strong>J</strong> and <strong>Z</strong> require spatial hand motion trajectories.
            Because SignAI utilizes a 2D static convolutional network, these two classes are approximated via static keyframe snapshots.
          </p>
        </div>
      </div>

      {/* Alphabet Grid (5 cols desktop, 4 cols md, 3 cols sm, 2 cols mobile) */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3.5 sm:gap-4">
        {filteredLetters.map((letter) => {
          const meta = ALPHABET_METADATA[letter] || {};
          return (
            <div
              key={letter}
              onClick={() => setActiveModalLetter(letter)}
              className="card-linear-hover p-4 flex flex-col justify-between cursor-pointer group shadow-sm"
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-2.5">
                <span className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-600 to-violet-600 text-white font-bold text-sm font-mono flex items-center justify-center shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform">
                  {letter}
                </span>

                <div className="flex flex-col items-end space-y-0.5">
                  <span
                    className={`font-mono text-[9px] uppercase font-bold px-2 py-0.5 rounded-full border ${
                      meta.difficulty === 'Easy'
                        ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800'
                        : meta.difficulty === 'Dynamic'
                        ? 'bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800'
                        : meta.difficulty === 'Hard'
                        ? 'bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 border-rose-200 dark:border-rose-800'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700'
                    }`}
                  >
                    {meta.difficulty}
                  </span>
                  <span className="text-[10px] font-mono font-medium text-slate-500 dark:text-slate-400">
                    {meta.acc} Acc
                  </span>
                </div>
              </div>

              {/* Reference Image Container */}
              <div className="relative aspect-square rounded-xl overflow-hidden bg-slate-950 border border-slate-800/80 mb-2.5 flex items-center justify-center">
                <img
                  src={`/alphabet_samples/${letter}.jpg`}
                  alt={`ISL Hand Sign for letter ${letter}`}
                  loading="lazy"
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                {meta.isDynamic && (
                  <span className="absolute bottom-1.5 right-1.5 text-[9px] font-mono font-bold bg-slate-950/85 backdrop-blur-xs text-indigo-300 px-1.5 py-0.5 rounded border border-white/10">
                    Keyframe
                  </span>
                )}
              </div>

              {/* Description */}
              <p className="text-xs text-slate-600 dark:text-slate-400 line-clamp-2 leading-relaxed">
                {meta.desc}
              </p>
            </div>
          );
        })}
      </div>

      {filteredLetters.length === 0 && (
        <div className="card-linear p-8 text-center text-slate-500 dark:text-slate-400 font-mono text-xs">
          No alphabet classes match query &ldquo;{searchQuery}&rdquo;.
        </div>
      )}

      {/* Selected Letter Detail Modal */}
      {activeModalLetter && selectedMeta && (
        <Modal
          isOpen={Boolean(activeModalLetter)}
          onClose={() => setActiveModalLetter(null)}
          title={`ISL Alphabet Letter '${activeModalLetter}' Specification`}
          maxWidth="max-w-xl"
        >
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 items-center">
              {/* Left Column: Reference Image */}
              <div className="relative aspect-square rounded-xl overflow-hidden bg-slate-950 border border-slate-800 flex items-center justify-center shadow-inner">
                <img
                  src={`/alphabet_samples/${activeModalLetter}.jpg`}
                  alt={`Detailed view of ISL letter ${activeModalLetter}`}
                  className="w-full h-full object-cover"
                />
              </div>

              {/* Right Column: Metas and Descriptions */}
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 text-white font-mono font-bold text-3xl flex items-center justify-center shadow-lg shadow-indigo-500/25">
                    {activeModalLetter}
                  </div>
                  <div>
                    <h4 className="text-base font-bold text-slate-900 dark:text-white">
                      Letter '{activeModalLetter}'
                    </h4>
                    <span className="font-mono text-xs text-indigo-600 dark:text-indigo-400 font-semibold">
                      Independent Test Accuracy: {selectedMeta.acc}
                    </span>
                  </div>
                </div>

                <div className="space-y-1">
                  <span className="text-[10px] uppercase tracking-wider text-slate-400 dark:text-slate-500 font-bold block">
                    Biomechanical Orientation
                  </span>
                  <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
                    {selectedMeta.desc}
                  </p>
                </div>

                {selectedMeta.isDynamic && (
                  <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-700 dark:text-indigo-300 font-mono">
                    <strong>Motion Note:</strong> Dynamic air stroke approximated via stationary keyframe pose.
                  </div>
                )}
              </div>
            </div>

            {/* Modal Actions */}
            <div className="flex items-center justify-end space-x-2 pt-4 border-t border-slate-200/80 dark:border-white/[0.08]">
              <button
                type="button"
                onClick={() => setActiveModalLetter(null)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/[0.04] transition-colors"
              >
                Close
              </button>

              <button
                type="button"
                onClick={() => handlePracticeInStudio(activeModalLetter)}
                className="btn-indigo text-xs"
              >
                <span>Practice in Studio</span>
                <ArrowRight className="w-3.5 h-3.5 ml-1" />
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}