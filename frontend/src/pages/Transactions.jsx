/**
 * Transactions page — paginated list, filter bar, create/edit/delete.
 */
import { useState, useEffect, useCallback } from "react";
import { Plus } from "lucide-react";
import toast from "react-hot-toast";
import { useApp } from "../context/AppContext";
import {
    getTransactions,
    createTransaction,
    updateTransaction,
    deleteTransaction,
} from "../api/transactions";
import TransactionItem from "../components/TransactionItem";
import TransactionForm from "../components/TransactionForm";

const PAGE_SIZE = 20;

export default function Transactions() {
    const { categories } = useApp();
    const [transactions, setTransactions] = useState([]);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(0);
    const [filters, setFilters] = useState({ type: "", category_id: "" });
    const [showForm, setShowForm] = useState(false);
    const [editing, setEditing] = useState(null);

    const load = useCallback(async () => {
        try {
            const params = {
                limit: PAGE_SIZE,
                offset: page * PAGE_SIZE,
                ...(filters.type && { type: filters.type }),
                ...(filters.category_id && { category_id: filters.category_id }),
            };
            const res = await getTransactions(params);
            setTransactions(res.data);
            setTotal(res.total);
        } catch (e) {
            toast.error(e.message);
        }
    }, [page, filters]);

    useEffect(() => { load(); }, [load]);

    const handleCreate = async (data) => {
        try {
            await createTransaction(data);
            toast.success("Transaction added");
            setShowForm(false);
            load();
        } catch (e) {
            toast.error(e.message);
        }
    };

    const handleUpdate = async (data) => {
        try {
            await updateTransaction(editing.id, data);
            toast.success("Updated");
            setEditing(null);
            load();
        } catch (e) {
            toast.error(e.message);
        }
    };

    const handleDelete = async (id) => {
        if (!confirm("Delete this transaction?")) return;
        try {
            await deleteTransaction(id);
            toast.success("Deleted");
            load();
        } catch (e) {
            toast.error(e.message);
        }
    };

    const totalPages = Math.ceil(total / PAGE_SIZE);

    return (
        <div>
            <div className="flex items-center gap-2 mb-6">
                <h1 className="page-title" style={{ margin: 0 }}>Transactions</h1>
                <button
                    className="btn btn-primary ml-auto"
                    onClick={() => setShowForm(true)}
                >
                    <Plus size={15} /> Add
                </button>
            </div>

            {/* Filters */}
            <div className="filters-row">
                <select
                    className="form-select"
                    style={{ width: "auto" }}
                    value={filters.type}
                    onChange={(e) =>
                        setFilters((f) => ({ ...f, type: e.target.value })) || setPage(0)
                    }
                >
                    <option value="">All types</option>
                    <option value="income">Income</option>
                    <option value="expense">Expense</option>
                </select>
                <select
                    className="form-select"
                    style={{ width: "auto" }}
                    value={filters.category_id}
                    onChange={(e) =>
                        setFilters((f) => ({ ...f, category_id: e.target.value })) || setPage(0)
                    }
                >
                    <option value="">All categories</option>
                    {categories.map((c) => (
                        <option key={c.id} value={c.id}>
                            {c.icon} {c.name}
                        </option>
                    ))}
                </select>
                <span className="text-muted ml-auto">{total} total</span>
            </div>

            <div className="card">
                {transactions.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-state-icon">📭</div>
                        <div>
                            You don&apos;t have any transactions that match
                            these filters yet.
                        </div>
                    </div>
                ) : (
                    <div className="tx-list">
                        {transactions.map((tx) => (
                            <TransactionItem
                                key={tx.id}
                                tx={tx}
                                onEdit={(t) => setEditing(t)}
                                onDelete={handleDelete}
                            />
                        ))}
                    </div>
                )}

                {totalPages > 1 && (
                    <div className="pagination">
                        <button
                            className="btn btn-ghost"
                            disabled={page === 0}
                            onClick={() => setPage((p) => p - 1)}
                        >
                            ← Prev
                        </button>
                        <span>
                            {page + 1} / {totalPages}
                        </span>
                        <button
                            className="btn btn-ghost"
                            disabled={page >= totalPages - 1}
                            onClick={() => setPage((p) => p + 1)}
                        >
                            Next →
                        </button>
                    </div>
                )}
            </div>

            {showForm && (
                <TransactionForm onSubmit={handleCreate} onClose={() => setShowForm(false)} />
            )}
            {editing && (
                <TransactionForm
                    onSubmit={handleUpdate}
                    onClose={() => setEditing(null)}
                    initial={{
                        amount: editing.amount,
                        type: editing.type,
                        date: editing.date,
                        description: editing.description,
                        category_id: editing.category_id ?? "",
                    }}
                />
            )}
        </div>
    );
}
