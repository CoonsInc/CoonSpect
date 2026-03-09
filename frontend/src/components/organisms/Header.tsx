import { useState, useRef, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuthStore } from "../../stores/authStore";
import { useAppStore } from "../../stores/appStore";
import { Menu, LogOut, User, Upload, Home, FileText, Sun, Moon, LogIn } from "lucide-react";


const Header: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const { theme, setTheme } = useAppStore();
  const [menuOpen, setMenuOpen] = useState(false);
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const profileMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (profileMenuRef.current && !profileMenuRef.current.contains(event.target as Node)) {
        setProfileMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const scrollTo = (id: string) => {
    const isMainPage = location.pathname === "/" || location.pathname === "/upload";
    
    if (id === "hero") {
      if (location.pathname !== "/") {
        navigate("/");
        setTimeout(() => window.scrollTo({ top: 0, behavior: "smooth" }), 100);
      } else {
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
      setMenuOpen(false);
      return;
    }

    if (!isMainPage) {
      navigate("/");
      setTimeout(() => document.getElementById(id)?.scrollIntoView({ behavior: "smooth" }), 100);
    } else {
      document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
    }
    setMenuOpen(false);
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    setMenuOpen(false);
    setProfileMenuOpen(false);
  };

  const handleLogout = async () => {
    await logout();
    navigate("/");
    setProfileMenuOpen(false);
    setMenuOpen(false);
  };

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
    document.documentElement.classList.toggle('dark');
  };

  const navItems = [
    { id: "hero", label: "Главная", icon: Home, mobileOnly: false },
    { id: "how", label: "Как это работает", icon: FileText, mobileOnly: false },
    { id: "examples", label: "Примеры", icon: Upload, mobileOnly: false },
    { path: "/files", label: "Мои файлы", icon: FileText, mobileOnly: false },
  ];

  return (
    <header className="fixed top-0 left-0 w-full bg-[var(--color-bg-accent)]/80 backdrop-blur-md border-b border-[var(--color-border)] z-50">
      <div className="max-w-7xl mx-auto flex justify-between items-center py-4 px-6">
        {/* Logo */}
        <h1
          onClick={() => handleNavigation("/")}
          className="text-2xl font-semibold text-[var(--color-text-purple)] cursor-pointer hover:opacity-80 transition"
        >
          CoonSpect
        </h1>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-6 text-sm text-[var(--color-text-secondary)]">
          {navItems.map((item) => (
            <button
              key={item.id || item.path}
              onClick={() => item.path ? handleNavigation(item.path) : scrollTo(item.id!)}
              className="hover:text-[var(--color-text-purple)] transition"
            >
              {item.label}
            </button>
          ))}

          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="hover:text-[var(--color-text-purple)] transition p-1"
            aria-label="Переключить тему"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>

          {/* User Menu */}
          {user ? (
            <div className="relative" ref={profileMenuRef}>
              <button
                className="flex items-center gap-2 hover:text-[var(--color-text-purple)] transition"
                onClick={() => setProfileMenuOpen(!profileMenuOpen)}
              >
                <User className="w-4 h-4" />
                <span className="max-w-[100px] truncate">{user.username}</span>
              </button>
              
              {profileMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-[var(--color-bg-accent)] border border-[var(--color-border)] rounded-lg shadow-lg overflow-hidden">
                  <button
                    onClick={() => handleNavigation("/profile")}
                    className="flex items-center gap-2 w-full px-4 py-3 text-sm text-left hover:bg-[var(--color-bg-secondary)] transition border-b border-[var(--color-border)]"
                  >
                    <User className="w-4 h-4" /> Профиль
                  </button>
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 w-full px-4 py-3 text-sm text-left hover:bg-[var(--color-bg-secondary)] transition"
                  >
                    <LogOut className="w-4 h-4" /> Выйти
                  </button>
                </div>
              )}
            </div>
          ) : (
            <button
              onClick={() => handleNavigation("/login")}
              className="flex items-center gap-1 hover:text-[var(--color-text-purple)] transition"
            >
              <LogIn className="w-4 h-4" /> Войти
            </button>
          )}
        </nav>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden text-[var(--color-text-secondary)] hover:text-[var(--color-text-purple)] transition"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Меню"
        >
          <Menu className="w-6 h-6" />
        </button>
      </div>

      {/* Mobile Menu */}
      {menuOpen && (
        <div className="md:hidden bg-[var(--color-bg-accent)] border-t border-[var(--color-border)] py-3 px-6 text-[var(--color-text-secondary)]">
          <div className="space-y-2">
            {navItems.map((item) => (
              <button
                key={item.id || item.path}
                onClick={() => item.path ? handleNavigation(item.path) : scrollTo(item.id!)}
                className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg hover:bg-[var(--color-bg-secondary)] hover:text-[var(--color-text-purple)] transition"
              >
                <item.icon className="w-4 h-4" />
                {item.label}
              </button>
            ))}

            {/* Mobile Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg hover:bg-[var(--color-bg-secondary)] hover:text-[var(--color-text-purple)] transition"
            >
              {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
              {theme === 'dark' ? 'Светлая тема' : 'Темная тема'}
            </button>

            <div className="border-t border-[var(--color-border)] my-2" />

            {/* Mobile User Menu */}
            {user ? (
              <>
                <button
                  onClick={() => handleNavigation("/profile")}
                  className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg hover:bg-[var(--color-bg-secondary)] hover:text-[var(--color-text-purple)] transition"
                >
                  <User className="w-4 h-4" /> Профиль
                </button>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg hover:bg-[var(--color-bg-secondary)] hover:text-[var(--color-text-purple)] transition"
                >
                  <LogOut className="w-4 h-4" /> Выйти
                </button>
              </>
            ) : (
              <button
                onClick={() => handleNavigation("/login")}
                className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg hover:bg-[var(--color-bg-secondary)] hover:text-[var(--color-text-purple)] transition"
              >
                <LogIn className="w-4 h-4" /> Войти
              </button>
            )}
          </div>
        </div>
      )}
    </header>
  );
};

export default Header;