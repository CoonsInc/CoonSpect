// компонент с spinner

import Spinner from "../atoms/Spinner";
import Heading from "../atoms/Heading";
import Text from "../atoms/Text";

const LoadingSection: React.FC = () => {
    return (
        <section className="flex flex-col justify-center items-center min-h-[60vh]">
            <Spinner size={12} />
            <Heading level={2} className="mt4">Генерация конспекта...</Heading>
            <Text size="sm" className="text-gray-400 mt-2">Это может занять немного времени...</Text>
        </section>
    );
};

export default LoadingSection;