import React from 'react';
import { useNavigate } from 'react-router-dom';
import Icon, { type IconName } from '../atoms/Icon';
import Heading from '../atoms/Heading';
import Text from '../atoms/Text';
import Button from '../atoms/Button';

export interface Lecture {
  id: string;
  title: string;
  description: string;
  duration: number;
  level: 'beginner' | 'intermediate' | 'advanced';
  icon: IconName;
}

interface LectureCardProps {
  lecture: Lecture;
}

const LectureCard: React.FC<LectureCardProps> = ({ lecture }) => {
  const navigate = useNavigate();

  return (
    <div className="group bg-[var(--color-bg-secondary)] rounded-lg p-6 border border-[var(--color-border)] hover:border-[var(--color-text-purple)] transition-all duration-300 hover:shadow-lg flex flex-col h-full">
      <div className="flex justify-between items-start mb-4">
        <div className="p-2 bg-[var(--color-text-purple)]/10 rounded-lg group-hover:bg-[var(--color-text-purple)]/20 transition-colors">
          <Icon name={lecture.icon} className="w-6 h-6 text-[var(--color-text-purple)]" />
        </div>
      </div>

      <div className="flex-1">
        <Heading level={4} className="text-xl font-semibold mb-2 text-[var(--color-text-primary)]">
          {lecture.title}
        </Heading>
        <Text size="sm" className="text-[var(--color-text-secondary)] mb-4">
          {lecture.description}
        </Text>
      </div>

      <div className="mt-6 flex items-center justify-between border-t border-[var(--color-border)] pt-4">
        <div className="flex items-center gap-2">
          <Icon name="Clock" className="w-4 h-4 text-[var(--color-text-secondary)]" />
          <Text size="sm" className="font-medium">{lecture.duration} мин</Text>
        </div>
        
        <Button 
          variant="primary" 
          size="sm" 
          onClick={() => navigate(`/editor/${lecture.id}`)}
        >
          Открыть конспект
        </Button>
      </div>
    </div>
  );
};

export default LectureCard;
