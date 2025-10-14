import Heading from "../atoms/Heading";
import HowItWorksStep from "../molecules/HowItWorksStep";

const HowItWorksSection: React.FC = () => {
  return (
    <section
      id="how"
      className="py-24 bg-[#10112A] text-center flex flex-col items-center"
    >
      <Heading level={2} className="text-purple-400 mb-12 text-3xl font-bold">
        Как это работает
      </Heading>
      <div className="grid sm:grid-cols-3 gap-12 max-w-5xl px-6">
        <HowItWorksStep icon="Upload" text="Загрузи аудио лекции или подкаста" />
        <HowItWorksStep icon="Loader2" text="AI проанализирует и создаст конспект" />
        <HowItWorksStep icon="Edit3" text="Отредактируй и сохрани результат" />
      </div>
    </section>
  );
};

export default HowItWorksSection;
