import Spinner from "../atoms/Spinner";
import Heading from "../atoms/Heading";
import Text from "../atoms/Text";

const LoadingSection: React.FC = () => {
    return (
        <section className="flex flex-col justify-center items-center min-h-[60vh]">
            <Spinner size={12} />
            <Heading level={2} className="mt-4 text-purple-400">Обрабатываем аудио...</Heading>
            <Text size="sm" className="text-gray-400 mt-2">Это может занять несколько секунд</Text>
            <div className="mt-6 bg-gray-700 rounded-full w-64 h-2">
                <div className="bg-purple-500 h-2 rounded-full animate-pulse w-3/4"></div>
            </div>
            <Text size="sm" className="text-gray-500 mt-2">Демо-режим: имитация работы AI</Text>
        </section>
    );
};

export default LoadingSection;