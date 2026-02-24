/**
 * Budgets page — shows budget vs actuals for selected month.
 */
import { useState, useEffect } from "react";
import { Plus, Trash2 } from "lucide-react";
import toast from "react-hot-toast";
import { useApp } from "../context/AppContext";
import { getBudgets, createBudget, deleteBudget } from "../api/budgets";

const cleanCategoryName = (name) => {
    if (!name) return "";
    // Strip emoji / non-word symbols so names look clean in all fonts
    return name
        .replace(/[^\w\s&-]/g, "")
        .replace(/\s+/g, " ")
        .trim();
};

function BudgetCard({ b, onDelete }) {
    const pct = b.utilization_pct ?? 0;
    const color =
        pct >= 100 ? "#ef4444" : pct >= 80 ? "#f59e0b" : "#22c55e";

    const displayName = cleanCategoryName(b.category?.name) || "Uncategorised";

    return (
        <div className="budget-card">
            <div className="budget-card-header">
                <div className="budget-category">
                    <span>{displayName}</span>
                </div>
                <button
                    className="btn btn-danger"
                    style={{ padding: "4px 8px" }}
                    onClick={() => onDelete(b.id)}
                >
                    <Trash2 size={13} />
                </button>
            </div>

            <div className="progress-bar-track">
                <div
                    className="progress-bar-fill"
                    style={{
                        width: `${Math.min(pct, 100)}%`,
                        background: color,
                    }}
                />
            </div>

            <div className="budget-meta">
                <span style={{ color }}>
                    {pct.toFixed(0)}% used · ₹{(b.spent ?? 0).toFixed(0)} spent
                </span>
                <span>Limit: ₹{b.limit_amount.toFixed(0)}</span>
            </div>
        </div>
    );
}

function BudgetForm({ categories, month, usedCategoryIds = [], onSubmit, onClose }) {
    const [form, setForm] = useState({
        category_id: "",
        month,
        limit_amount: "",
    });

    const set = (f) => (e) => setForm((p) => ({ ...p, [f]: e.target.value }));

    const handleSubmit = async (e) => {
        e.preventDefault();
        await onSubmit({
            category_id: parseInt(form.category_id),
            month: form.month,
            limit_amount: parseFloat(form.limit_amount),
        });
    };

    return (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
            <div className="modal">
                <h2 className="modal-title">New Budget</h2>
                <form onSubmit={handleSubmit}>
                    <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
                        <div className="form-group">
                            <label className="form-label">Category</label>
                            <select
                                className="form-select"
                                required
                                value={form.category_id}
                                onChange={set("category_id")}
                            >
                                <option value="">Choose a category…</option>
                                {categories.map((c) => {
                                    const isUsed = usedCategoryIds.includes(c.id);
                                    const label = cleanCategoryName(c.name) || "Unnamed category";
                                    return (
                                        <option key={c.id} value={c.id} disabled={isUsed}>
                                            {label}
                                            {isUsed ? " (already has a budget this month)" : ""}
                                        </option>
                                    );
                                })}
                            </select>
                            <div className="form-help">
                                You can have only one budget per category for a
                                given month. Categories that already have a budget
                                are greyed out.
                            </div>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Month</label>
                            <input className="form-input" type="month" required value={form.month} onChange={set("month")} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Limit (₹)</label>
                            <input className="form-input" type="number" min="0.01" step="0.01" required value={form.limit_amount} onChange={set("limit_amount")} />
                        </div>
                    </div>
                    <div className="modal-footer">
                        <button type="button" className="btn btn-ghost" onClick={onClose}>Cancel</button>
                        <button type="submit" className="btn btn-primary">Create Budget</button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default function Budgets() {
    const { activeMonth, setActiveMonth, categories } = useApp();
    const [budgets, setBudgets] = useState([]);
    const [showForm, setShowForm] = useState(false);

    const load = async () => {
        try {
            const data = await getBudgets({ month: activeMonth });
            setBudgets(data);
        } catch (e) {
            toast.error(e.message);
        }
    };

    useEffect(() => { load(); }, [activeMonth]);

    const handleCreate = async (data) => {
        try {
            await createBudget(data);
            toast.success("Budget created");
            setShowForm(false);
            load();
        } catch (e) {
            if (e.message && e.message.startsWith("Conflict:")) {
                toast.error(
                    "You already have a budget for this category in that month. Try editing the existing one instead."
                );
            } else {
                toast.error(e.message);
            }
        }
    };

    const handleDelete = async (id) => {
        if (!confirm("Delete this budget?")) return;
        try {
            await deleteBudget(id);
            toast.success("Budget removed");
            load();
        } catch (e) {
            toast.error(e.message);
        }
    };

    return (
        <div>
            <div className="flex items-center gap-2 mb-6">
                <h1 className="page-title" style={{ margin: 0 }}>Budgets</h1>
                <div className="month-picker ml-auto">
                    <input
                        type="month"
                        value={activeMonth}
                        onChange={(e) => setActiveMonth(e.target.value)}
                    />
                </div>
                <button className="btn btn-primary" onClick={() => setShowForm(true)}>
                    <Plus size={15} /> Add
                </button>
            </div>

            {budgets.length === 0 ? (
                <div className="empty-state" style={{ marginTop: 60 }}>
                    <div className="empty-state-icon">🎯</div>
                    <div>
                        You haven&apos;t set any budgets for {activeMonth} yet.
                        Create one to give yourself a gentle spending limit.
                    </div>
                </div>
            ) : (
                <div className="budget-grid">
                    {budgets.map((b) => (
                        <BudgetCard key={b.id} b={b} onDelete={handleDelete} />
                    ))}
                </div>
            )}

            {showForm && (
                <BudgetForm
                    categories={categories}
                    month={activeMonth}
                    usedCategoryIds={budgets.map((b) => b.category_id)}
                    onSubmit={handleCreate}
                    onClose={() => setShowForm(false)}
                />
            )}
        </div>
    );
}
