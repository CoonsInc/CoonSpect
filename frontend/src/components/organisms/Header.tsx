const Header: React.FC = () => {
  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <header className="fixed top-0 left-0 w-full bg-[#0B0C1C]/80 backdrop-blur-md border-b border-purple-800/30 z-50">
      <div className="max-w-6xl mx-auto flex justify-between items-center py-4 px-6">
        <h1 className="text-2xl font-semibold text-purple-400">AudioNotes AI</h1>
        <nav className="flex gap-6 text-sm">
          <button onClick={() => scrollTo("hero")} className="hover:text-purple-400 transition">
            Главная
          </button>
          <button onClick={() => scrollTo("how")} className="hover:text-purple-400 transition">
            Как это работает
          </button>
          <button onClick={() => scrollTo("examples")} className="hover:text-purple-400 transition">
            Примеры
          </button>
        </nav>
      </div>
    </header>
  );
};

export default Header;
