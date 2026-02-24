/**
 * Dashboard page — shows current-month summary, recent transactions.
 */
import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { TrendingUp, TrendingDown, IndianRupee, ArrowRight, Plus } from "lucide-react";
import { useApp } from "../context/AppContext";
import { getSummary } from "../api/analytics";
import { getTransactions } from "../api/transactions";
import SummaryCard from "../components/SummaryCard";
import TransactionItem from "../components/TransactionItem";

export default function Dashboard() {
    const { activeMonth, setActiveMonth } = useApp();
    const navigate = useNavigate();
    const [summary, setSummary] = useState(null);
    const [recent, setRecent] = useState([]);

    useEffect(() => {
        getSummary(activeMonth).then(setSummary).catch(() => { });
        // Compute the real last day of the month to avoid invalid dates like Feb-31
        const [yr, mo] = activeMonth.split("-").map(Number);
        const lastDay = new Date(yr, mo, 0).getDate(); // day 0 of next month = last day of this month
        const dateTo = `${activeMonth}-${String(lastDay).padStart(2, "0")}`;
        getTransactions({ limit: 8, date_from: `${activeMonth}-01`, date_to: dateTo })
            .then((r) => setRecent(r.data))
            .catch(() => { });
    }, [activeMonth]);

    return (
        <div>
            <div className="flex items-center gap-3 mb-2">
                <div>
                    <h1 className="page-title" style={{ margin: 0 }}>Dashboard</h1>
                    <p className="text-muted" style={{ margin: 0, fontSize: "0.9rem" }}>
                        A quick overview of how your money is doing this month.
                    </p>
                </div>
                <div className="month-picker ml-auto">
                    <input
                        type="month"
                        value={activeMonth}
                        onChange={(e) => setActiveMonth(e.target.value)}
                    />
                </div>
                <button
                    className="btn btn-primary"
                    onClick={() => navigate("/transactions")}
                    style={{ whiteSpace: "nowrap" }}
                >
                    <Plus size={15} /> New transaction
                </button>
            </div>

            <div className="summary-grid">
                <SummaryCard
                    label="Total Income"
                    value={summary?.income ?? 0}
                    icon={<TrendingUp size={18} color="#22c55e" />}
                    variant="income"
                />
                <SummaryCard
                    label="Total Expenses"
                    value={summary?.expense ?? 0}
                    icon={<TrendingDown size={18} color="#ef4444" />}
                    variant="expense"
                />
                <SummaryCard
                    label="Net Balance"
                    value={summary?.net ?? 0}
                    icon={<IndianRupee size={18} color="#818cf8" />}
                    variant="net"
                />
            </div>

            <div className="card">
                <div className="section-header">
                    <span className="section-title">Recent Transactions</span>
                    <Link to="/transactions" className="btn btn-ghost" style={{ fontSize: "0.8rem" }}>
                        View all <ArrowRight size={13} />
                    </Link>
                </div>
                {recent.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-state-icon">🧾</div>
                        <div>No transactions this month</div>
                    </div>
                ) : (
                    <div className="tx-list">
                        {recent.map((tx) => (
                            <TransactionItem key={tx.id} tx={tx} />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
