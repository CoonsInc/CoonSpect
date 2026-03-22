
import { useEffect } from "react";
import { BrowserRouter as Router } from "react-router-dom";
import AppRoutes from "./routes";
import { useAuthStore } from "./stores/authStore";
import { useAppStore } from "./stores/appStore";

const App = () => {
  const { initialize } = useAuthStore();
  const { theme } = useAppStore();

  useEffect(() => {
    initialize();
  }, [initialize]);

  useEffect(() => {
    const root = document.documentElement;
    
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }

    localStorage.setItem('theme', theme);
  }, [theme]);

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
    if (savedTheme && savedTheme !== theme) {
      useAppStore.getState().setTheme(savedTheme);
    }
  }, []);

  return (
    <Router>
      <AppRoutes />
    </Router>
  );
};

export default App;
