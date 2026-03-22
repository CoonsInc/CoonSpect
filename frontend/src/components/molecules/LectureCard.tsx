import React from 'react';
import Icon from '../atoms/Icon';
import Heading from '../atoms/Heading';
import Text from '../atoms/Text';
import type { Lecture } from '../../types/lecture'; // Проверь правильность пути до файла с типами!

interface LectureCardProps {
  lecture: Lecture;
  onClick: () => void;
}

const LectureCard: React.FC<LectureCardProps> = ({ lecture, onClick }) => {
  return (
    <div 
      onClick={onClick}
      className="flex flex-col p-5 bg-[var(--color-bg-accent)] rounded-xl border border-[var(--color-border)] shadow-sm hover:shadow-md hover:border-[var(--color-text-purple)] transition-all cursor-pointer group relative h-full"
    >
      <div className="mb-4">
        <Heading level={4} className="text-lg font-semibold group-hover:text-[var(--color-text-purple)] transition-colors line-clamp-2 mb-2">
          {lecture.name || 'Лекция без названия'}
        </Heading>
        
        <div className="space-y-1">
          {lecture.lecturer && (
            <Text className="text-sm text-[var(--color-text-secondary)]">
              <span className="font-medium text-[var(--color-text-primary)]">Лектор: </span> 
              {lecture.lecturer}
            </Text>
          )}
          
          <Text className="text-sm text-[var(--color-text-secondary)]">
            <span className="font-medium text-[var(--color-text-primary)]">Создатель: </span> 
            {lecture.user?.username || 'Неизвестен'}
          </Text>
        </div>
      </div>

      <div className="mt-auto pt-4 border-t border-[var(--color-border)] flex flex-col gap-3">
        <div className="flex flex-col text-xs text-[var(--color-text-secondary)] gap-1">
          <div className="flex justify-between items-center">
            <span>Создано:</span>
            <span className="font-medium text-[var(--color-text-primary)]">
              {new Date(lecture.created_at).toLocaleDateString('ru-RU')}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span>Изменено:</span>
            <span className="font-medium text-[var(--color-text-primary)]">
              {new Date(lecture.updated_at).toLocaleDateString('ru-RU')}
            </span>
          </div>
        </div>

        <div className="flex items-center justify-end text-sm font-medium text-[var(--color-text-secondary)] group-hover:text-[var(--color-text-purple)] transition-colors mt-1">
          Открыть конспект <Icon name="ArrowRight" className="w-4 h-4 ml-1" />
        </div>
      </div>
    </div>
  );
};

export default LectureCard;
