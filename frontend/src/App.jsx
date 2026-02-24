import { Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import Transactions from "./pages/Transactions";
import Budgets from "./pages/Budgets";
import Analytics from "./pages/Analytics";

export default function App() {
  return (
    <div className="app-shell">
      <Navbar />
      <main className="page-content">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/transactions" element={<Transactions />} />
          <Route path="/budgets" element={<Budgets />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </main>
    </div>
  );
}
