// блок с иконкой и текстом типо инструкция
import Icon from "../atoms/Icon";
import Text from "../atoms/Text";

interface HowItWorksStepProps {
    icon: "Upload" | "Edit3" | "Loader2";
    text: string;
}

const HowItWorksStep: React.FC<HowItWorksStepProps> = ({ icon, text }) => (
    <div className="flex flex-col items-center text-center max-w-[180px]">
        <Icon name={icon} className="w-8 h-8 text-purple-400 mb-2" />
        <Text>{text}</Text>
    </div>
);

export default HowItWorksStep;