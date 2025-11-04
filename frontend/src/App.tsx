import { BrowserRouter as Router } from 'react-router-dom';
import { UserProvider } from "./contexts/UserContext";
import AppRoutes from './routes';

const App = () => {
  return (
    <UserProvider>
      <Router>
        <AppRoutes />
      </Router>
    </UserProvider>
  );
};

export default App;