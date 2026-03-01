import Heading from "../atoms/Heading";
import Text from "../atoms/Text";

const ExamplesSection: React.FC = () => {
  const examples = [
    {
      title: "Лекция по физике",
      desc: "Подробный пересказ формул и теорий из университетской лекции.",
    },
    {
      title: "Подкаст о маркетинге",
      desc: "Конспект с ключевыми идеями и советами для бизнеса.",
    },
    {
      title: "Интервью с учёным",
      desc: "Сжатое изложение смыслов и выводов из интервью.",
    },
  ];

  return (
    <section id="examples" className="py-24 bg-[var(--color-bg-primary)] text-center">
      <Heading level={2} className="text-[var(--color-text-purple)] mb-12 text-3xl font-bold">
        Примеры конспектов
      </Heading>
      
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto px-6">
        {examples.map((example, index) => (
          <div
            key={index}
            className="group bg-[var(--color-bg-accent)] p-8 rounded-2xl border border-[var(--color-border)] hover:border-[var(--color-text-purple)] transition-all duration-300 hover:-translate-y-1 hover:shadow-lg"
          >
            <Text size="lg" className="text-[var(--color-text-primary)] font-semibold mb-3">
              {example.title}
            </Text>
            <Text size="sm" className="text-[var(--color-text-secondary)] leading-relaxed">
              {example.desc}
            </Text>
          </div>
        ))}
      </div>
    </section>
  );
};

export default ExamplesSection;
