import React, { useState } from "react";
import Icon from "../atoms/Icon";
import Text from "../atoms/Text";
import Heading from "../atoms/Heading";
import Spinner from "../atoms/Spinner"; 
import { formatSecondsToTime } from "../../utils/timeUtils";
import { useSearchStore } from '../../stores/searchStore';
import { useTextStore } from '../../stores';

// Интерфейс ответа от твоего FastAPI
// interface SearchResult {
//   score: number;
//   start: number;
//   end: number;
//   text: string;
// }

interface AudioSearchPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onTimeClick: (time: number) => void;
}

const AudioSearchPanel: React.FC<AudioSearchPanelProps> = ({ isOpen, onClose, onTimeClick }) => {
  const [query, setQuery] = useState('');
  const { results, isLoading, error, search, clearResults } = useSearchStore();
  const { activeLectureId } = useTextStore();

  const handleSearch = async () => {
    if (!query.trim() || !activeLectureId) return;
    await search(activeLectureId, query);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleClose = () => {
    clearResults();
    setQuery('');
    onClose();
  };

  const sidebarClasses = `
    fixed top-0 right-0 h-full w-full sm:w-[400px] 
    bg-[var(--color-bg-accent)] border-l border-[var(--color-border)] 
    shadow-2xl z-50 transform transition-transform duration-300 ease-in-out
    flex flex-col
    ${isOpen ? "translate-x-0" : "translate-x-full"}
  `;

  return (
    <>
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 transition-opacity" 
          onClick={handleClose}
        />
      )}

      <div className={sidebarClasses}>
        <div className="flex items-center justify-between p-5 border-b border-[var(--color-border)]">
          <Heading level={2} className="text-xl font-semibold text-[var(--color-text-purple)]">
            Поиск по аудио
          </Heading>
          <button 
            onClick={handleClose} 
            className="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
          >
            <Icon name="X" className="w-6 h-6" /> 
          </button>
        </div>

        <div className="p-5 border-b border-[var(--color-border)] flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Что вы хотите найти в лекции?"
            className="flex-grow bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] px-4 py-2 rounded-lg border border-[var(--color-border)] outline-none focus:border-[var(--color-text-purple)] transition-all text-sm disabled:opacity-50"
          />
          <button 
            onClick={handleSearch}
            disabled={isLoading || !query.trim() || !activeLectureId}
            className="bg-[var(--color-text-purple)] text-white px-4 py-2 rounded-lg hover:bg-[var(--color-text-purple)]/80 transition-colors disabled:opacity-50 flex items-center justify-center"
          >
            {isLoading ? <Spinner size="sm" /> : <Icon name="Search" className="w-4 h-4" />}
          </button>
        </div>

        {/* Результаты (скроллящаяся область) */}
        <div className="flex-grow overflow-y-auto p-5">
          {!activeLectureId && (
            <div className="text-center mt-10 text-[var(--color-text-secondary)]">
              <Icon name="FileAudio" className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <Text>Аудиофайл не загружен.<br/>Поиск недоступен.</Text>
            </div>
          )}

          {activeLectureId && !isLoading && results.length === 0 && !error && (
            <div className="text-center mt-10 text-[var(--color-text-secondary)]">
              <Icon name="Search" className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <Text>Введите запрос, например:<br/>"про градиентный спуск"</Text>
            </div>
          )}

          {error && (
            <div className="text-center mt-10 text-red-400 p-4 border border-red-900 rounded-lg bg-red-950/20">
              <Text size="sm">{error}</Text>
            </div>
          )}

          <div className="space-y-4">
            {results.map((result, index) => (
              <div 
                key={index} 
                className="bg-[var(--color-bg-primary)] p-4 rounded-lg border border-[var(--color-border)] hover:border-[var(--color-text-purple)]/50 transition-colors cursor-pointer"
                onClick={() => onTimeClick(result.start)}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-mono font-bold px-2 py-1 rounded bg-[var(--color-text-purple)]/10 text-[var(--color-text-purple)]">
                    {formatSecondsToTime(result.start)}
                  </span>
                  <span className="text-xs text-[var(--color-text-secondary)]">
                    score: {(result.score * 100).toFixed(0)}%
                  </span>
                </div>
                <Text size="sm" className="leading-relaxed text-[var(--color-text-primary)]">
                  {result.text}
                </Text>
                <div className="mt-2 text-right">
                    <span className="text-xs text-[var(--color-text-purple)] flex items-center justify-end gap-1 hover:underline">
                        <Icon name="Play" className="w-3 h-3"/> Слушать
                    </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
};

export default AudioSearchPanel;