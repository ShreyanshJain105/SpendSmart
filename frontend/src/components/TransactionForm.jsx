/**
 * TransactionForm — modal form for creating / editing a transaction.
 *
 * Calls the AI categorize endpoint after the user finishes typing the
 * description, and pre-fills the category dropdown if confidence is 1.0.
 */
import { useState, useEffect, useRef } from "react";
import { useApp } from "../context/AppContext";
import { categorizeDescription } from "../api/analytics";
import { Sparkles, X } from "lucide-react";

const EMPTY = {
    amount: "",
    type: "expense",
    date: new Date().toISOString().slice(0, 10),
    description: "",
    category_id: "",
};

export default function TransactionForm({ onSubmit, onClose, initial }) {
    const { categories } = useApp();
    const [form, setForm] = useState(initial ?? EMPTY);
    const [aiHint, setAiHint] = useState(null);
    const [loading, setLoading] = useState(false);
    const aiTimerRef = useRef(null);

    // Debounce AI call whenever description changes
    useEffect(() => {
        if (!form.description || form.description.length < 3) {
            setAiHint(null);
            return;
        }
        clearTimeout(aiTimerRef.current);
        aiTimerRef.current = setTimeout(async () => {
            try {
                const result = await categorizeDescription(form.description);
                if (result.confidence === 1.0) {
                    const match = categories.find(
                        (c) => c.name.toLowerCase() === result.category.toLowerCase()
                    );
                    if (match) {
                        setForm((f) => ({ ...f, category_id: match.id }));
                    }
                    setAiHint(result.category);
                } else {
                    setAiHint(null);
                }
            } catch {
                // Silently ignore AI errors — it's a best-effort feature
            }
        }, 600);
        return () => clearTimeout(aiTimerRef.current);
    }, [form.description, categories]);

    const set = (field) => (e) =>
        setForm((f) => ({ ...f, [field]: e.target.value }));

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await onSubmit({
                ...form,
                amount: parseFloat(form.amount),
                category_id: form.category_id ? parseInt(form.category_id) : null,
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
            <div className="modal">
                <div className="flex items-center gap-2 mb-4">
                    <h2 className="modal-title" style={{ margin: 0 }}>
                        {initial ? "Edit Transaction" : "New Transaction"}
                    </h2>
                    <button className="btn btn-ghost ml-auto" onClick={onClose} style={{ padding: "4px 8px" }}>
                        <X size={16} />
                    </button>
                </div>

                <form onSubmit={handleSubmit}>
                    <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
                        {/* Type toggle */}
                        <div className="form-group">
                            <label className="form-label">Type</label>
                            <div style={{ display: "flex", gap: "8px" }}>
                                {["expense", "income"].map((t) => (
                                    <button
                                        key={t}
                                        type="button"
                                        onClick={() => setForm((f) => ({ ...f, type: t }))}
                                        className="btn"
                                        style={{
                                            flex: 1,
                                            background:
                                                form.type === t
                                                    ? t === "expense"
                                                        ? "rgba(239,68,68,0.2)"
                                                        : "rgba(34,197,94,0.2)"
                                                    : "rgba(255,255,255,0.05)",
                                            color:
                                                form.type === t
                                                    ? t === "expense"
                                                        ? "#ef4444"
                                                        : "#22c55e"
                                                    : "#94a3b8",
                                            border: `1px solid ${form.type === t
                                                ? t === "expense"
                                                    ? "rgba(239,68,68,0.4)"
                                                    : "rgba(34,197,94,0.4)"
                                                : "transparent"
                                                }`,
                                        }}
                                    >
                                        {t === "expense" ? "↑ Expense" : "↓ Income"}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label className="form-label">Amount (₹)</label>
                                <input
                                    className="form-input"
                                    type="number"
                                    step="0.01"
                                    min="0.01"
                                    required
                                    placeholder="0.00"
                                    value={form.amount}
                                    onChange={set("amount")}
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Date</label>
                                <input
                                    className="form-input"
                                    type="date"
                                    required
                                    value={form.date}
                                    onChange={set("date")}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Description</label>
                            <input
                                className="form-input"
                                type="text"
                                placeholder="e.g. Groceries at the supermarket"
                                value={form.description}
                                onChange={set("description")}
                            />
                            {aiHint && (
                                <div className="ai-hint">
                                    <Sparkles size={11} /> AI suggested: <strong>{aiHint}</strong>
                                </div>
                            )}
                        </div>

                        <div className="form-group">
                            <label className="form-label">Category</label>
                            {categories.length === 0 ? (
                                <>
                                    <select
                                        className="form-select"
                                        value=""
                                        disabled
                                    >
                                        <option value="">
                                            No categories available yet
                                        </option>
                                    </select>
                                    <div className="form-help">
                                        You can still save this transaction without a
                                        category. Once categories are added, you’ll
                                        be able to organise your spending more
                                        clearly.
                                    </div>
                                </>
                            ) : (
                                <>
                                    <select
                                        className="form-select"
                                        value={form.category_id}
                                        onChange={set("category_id")}
                                    >
                                        <option value="">No category (optional)</option>
                                        {categories.map((c) => (
                                            <option key={c.id} value={c.id}>
                                                {c.icon} {c.name}
                                            </option>
                                        ))}
                                    </select>
                                    <div className="form-help">
                                        Picking a category is optional but helps make
                                        your reports and budgets more meaningful.
                                    </div>
                                </>
                            )}
                        </div>
                    </div>

                    <div className="modal-footer">
                        <button type="button" className="btn btn-ghost" onClick={onClose}>
                            Cancel
                        </button>
                        <button type="submit" className="btn btn-primary" disabled={loading}>
                            {loading ? "Saving…" : initial ? "Update" : "Add Transaction"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
