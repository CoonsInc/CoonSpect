import Icon from "../atoms/Icon";
import Text from "../atoms/Text";

interface HowItWorksStepProps {
  icon: "Upload" | "Edit3" | "Loader2";
  text: string;
  className?: string;
}

const HowItWorksStep: React.FC<HowItWorksStepProps> = ({ 
  icon, 
  text, 
  className = "" 
}) => (
  <div className={`flex flex-col items-center text-center max-w-[180px] ${className}`}>
    <div className="w-16 h-16 rounded-full bg-[var(--color-bg-secondary)] flex items-center justify-center mb-3">
      <Icon name={icon} className="w-8 h-8 text-[var(--color-text-purple)]" />
    </div>
    <Text className="text-[var(--color-text-secondary)] font-medium">
      {text}
    </Text>
  </div>
);

export default HowItWorksStep;
