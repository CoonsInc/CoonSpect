import React, { useState } from "react";
import Icon from "../atoms/Icon";
import Text from "../atoms/Text";
import Heading from "../atoms/Heading";
import Spinner from "../atoms/Spinner"; 
import { formatSecondsToTime } from "../../utils/timeUtils";

// Интерфейс ответа от твоего FastAPI
interface SearchResult {
  score: number;
  start: number;
  end: number;
  text: string;
}

interface AudioSearchPanelProps {
  isOpen: boolean;
  onClose: () => void;
  audioId: string | null;
  onTimeClick: (time: number) => void;
}

const AudioSearchPanel: React.FC<AudioSearchPanelProps> = ({
  isOpen,
  onClose,
  audioId,
  onTimeClick,
}) => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query.trim() || !audioId) return;

    setIsLoading(true);
    setError(null);
    setResults([]);

    try {
      // ЗАГЛУШКА
      // const response = await fetch(`/api/search?audio_id=${audioId}&query=${encodeURIComponent(query)}`);
      // const data = await response.json();
      
      await new Promise(res => setTimeout(res, 1000));
      const mockData: SearchResult[] = [
        { score: 0.92, start: 10.5, end: 20.0, text: "В этом фрагменте мы обсуждаем введение в нейронные сети и основные понятия." },
        { score: 0.85, start: 125.2, end: 140.0, text: "Формула градиентного спуска играет ключевую роль в обучении модели." },
        { score: 0.78, start: 300.0, end: 315.5, text: "Обратное распространение ошибки позволяет вычислять градиенты для всех весов." },
      ];

      setResults(mockData); 
      
      if (mockData.length === 0) {
        setError("Ничего не найдено по вашему запросу.");
      }
    } catch (e) {
      console.error("Search error:", e);
      setError("Произошла ошибка при поиске. Проверьте подключение к бэкенду.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
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
          onClick={onClose}
        />
      )}

      <div className={sidebarClasses}>
        <div className="flex items-center justify-between p-5 border-b border-[var(--color-border)]">
          <Heading level={2} className="text-xl font-semibold text-[var(--color-text-purple)]">
            Поиск по аудио
          </Heading>
          <button 
            onClick={onClose} 
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
            disabled={!audioId}
            className="flex-grow bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] px-4 py-2 rounded-lg border border-[var(--color-border)] outline-none focus:border-[var(--color-text-purple)] transition-all text-sm disabled:opacity-50"
          />
          <button 
            onClick={handleSearch}
            disabled={isLoading || !audioId || !query.trim()}
            className="bg-[var(--color-text-purple)] text-white px-4 py-2 rounded-lg hover:bg-[var(--color-text-purple)]/80 transition-colors disabled:opacity-50 flex items-center justify-center"
          >
            {isLoading ? <Spinner size="sm" /> : <Icon name="Search" className="w-4 h-4" />}
          </button>
        </div>

        {/* Результаты (скроллящаяся область) */}
        <div className="flex-grow overflow-y-auto p-5">
          {!audioId && (
            <div className="text-center mt-10 text-[var(--color-text-secondary)]">
               <Icon name="FileAudio" className="w-12 h-12 mx-auto mb-4 opacity-50" />
               <Text>Аудиофайл не загружен.<br/>Поиск недоступен.</Text>
            </div>
          )}

          {audioId && !isLoading && results.length === 0 && !error && (
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