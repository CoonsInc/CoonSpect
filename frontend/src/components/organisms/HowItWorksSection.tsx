
import Heading from "../atoms/Heading";
import HowItWorksStep from "../molecules/HowItWorksStep";

const HowItWorksSection: React.FC = () => {
  const steps = [
    { icon: "Upload" as const, text: "Загрузи аудио лекции или подкаста" },
    { icon: "Loader2" as const, text: "AI проанализирует и создаст конспект" },
    { icon: "Edit3" as const, text: "Отредактируй и сохрани результат" },
  ];

  return (
    <section id="how" className="py-24 bg-[var(--color-bg-primary)] text-center flex flex-col items-center">
      <Heading level={2} className="text-[var(--color-text-purple)] mb-12 text-3xl font-bold">
        Как это работает
      </Heading>
      
      <div className="grid sm:grid-cols-3 gap-12 max-w-5xl px-6">
        {steps.map((step, index) => (
          <HowItWorksStep key={index} icon={step.icon} text={step.text} />
        ))}
      </div>
    </section>
  );
};

export default HowItWorksSection;
