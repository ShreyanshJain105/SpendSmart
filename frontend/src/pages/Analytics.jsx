/**
 * Analytics page — bar chart (monthly trends) + pie chart (category breakdown).
 */
import { useState, useEffect } from "react";
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend,
    PieChart, Pie, Cell,
} from "recharts";
import { useApp } from "../context/AppContext";
import { getSummary, getBreakdown, getTrends } from "../api/analytics";

const COLORS = [
    "#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6",
    "#06b6d4", "#ec4899", "#14b8a6", "#f97316", "#84cc16",
];

const fmt$ = (v) =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(v);

function CustomTooltip({ active, payload, label }) {
    if (!active || !payload?.length) return null;
    return (
        <div className="card" style={{ padding: "10px 14px", borderColor: "#6366f1" }}>
            <div style={{ fontSize: "0.8rem", color: "#94a3b8", marginBottom: 4 }}>{label}</div>
            {payload.map((p) => (
                <div key={p.name} style={{ fontSize: "0.875rem", color: p.color }}>
                    {p.name}: {fmt$(p.value)}
                </div>
            ))}
        </div>
    );
}

export default function Analytics() {
    const { activeMonth, setActiveMonth } = useApp();
    const [summary, setSummary] = useState(null);
    const [breakdown, setBreakdown] = useState([]);
    const [trends, setTrends] = useState([]);

    useEffect(() => {
        getSummary(activeMonth).then(setSummary).catch(() => { });
        getBreakdown(activeMonth).then(setBreakdown).catch(() => { });
        getTrends(6).then(setTrends).catch(() => { });
    }, [activeMonth]);

    return (
        <div>
            <div className="flex items-center gap-3 mb-6">
                <h1 className="page-title" style={{ margin: 0 }}>Analytics</h1>
                <div className="month-picker ml-auto">
                    <input
                        type="month"
                        value={activeMonth}
                        onChange={(e) => setActiveMonth(e.target.value)}
                    />
                </div>
            </div>

            {/* Month summary */}
            {summary && (
                <div className="summary-grid mb-6">
                    {[
                        { label: "Income", value: fmt$(summary.income), color: "#22c55e" },
                        { label: "Expenses", value: fmt$(summary.expense), color: "#ef4444" },
                        { label: "Net", value: fmt$(summary.net), color: summary.net >= 0 ? "#22c55e" : "#ef4444" },
                    ].map(({ label, value, color }) => (
                        <div className="card" key={label} style={{ textAlign: "center" }}>
                            <div style={{ fontSize: "0.75rem", color: "#64748b", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.05em" }}>{label}</div>
                            <div style={{ fontSize: "1.5rem", fontWeight: 700, color }}>{value}</div>
                        </div>
                    ))}
                </div>
            )}

            <div className="charts-grid">
                {/* Monthly Trends Bar Chart */}
                <div className="card">
                    <div className="section-title mb-4">Monthly Trends</div>
                    {trends.length === 0 ? (
                        <div className="empty-state"><div className="empty-state-icon">📊</div><div>No data yet</div></div>
                    ) : (
                        <ResponsiveContainer width="100%" height={260}>
                            <BarChart data={trends} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
                                <XAxis dataKey="month" tick={{ fill: "#64748b", fontSize: 11 }} />
                                <YAxis tick={{ fill: "#64748b", fontSize: 11 }} tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`} />
                                <Tooltip content={<CustomTooltip />} />
                                <Legend
                                    wrapperStyle={{ fontSize: "0.75rem", color: "#94a3b8" }}
                                />
                                <Bar dataKey="income" name="Income" fill="#22c55e" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="expense" name="Expense" fill="#ef4444" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    )}
                </div>

                {/* Category breakdown Pie */}
                <div className="card">
                    <div className="section-title mb-4">Spending by Category</div>
                    {breakdown.length === 0 ? (
                        <div className="empty-state"><div className="empty-state-icon">🥧</div><div>No expense data this month</div></div>
                    ) : (
                        <>
                            <ResponsiveContainer width="100%" height={200}>
                                <PieChart>
                                    <Pie
                                        data={breakdown}
                                        dataKey="total"
                                        nameKey="category_name"
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={55}
                                        outerRadius={90}
                                        paddingAngle={3}
                                    >
                                        {breakdown.map((entry, i) => (
                                            <Cell
                                                key={entry.category_id}
                                                fill={entry.color ?? COLORS[i % COLORS.length]}
                                            />
                                        ))}
                                    </Pie>
                                    <Tooltip formatter={(v) => fmt$(v)} />
                                </PieChart>
                            </ResponsiveContainer>
                            <div style={{ display: "flex", flexDirection: "column", gap: "6px", marginTop: 8 }}>
                                {breakdown.map((b, i) => (
                                    <div key={b.category_id} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: "0.8rem" }}>
                                        <div style={{ width: 10, height: 10, borderRadius: "50%", background: b.color ?? COLORS[i % COLORS.length], flexShrink: 0 }} />
                                        <span style={{ color: "#94a3b8", flex: 1 }}>{b.icon} {b.category_name}</span>
                                        <span style={{ color: "#f1f5f9", fontWeight: 600 }}>{fmt$(b.total)}</span>
                                    </div>
                                ))}
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
