import { Trash2, Pencil } from "lucide-react";

const fmt = (n) =>
    new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
    }).format(n);

const cleanCategoryName = (name) => {
    if (!name) return "";
    return name
        .replace(/[^\w\s&-]/g, "")
        .replace(/\s+/g, " ")
        .trim();
};

export default function TransactionItem({ tx, onEdit, onDelete }) {
    const cat = tx.category;
    const categoryName = cleanCategoryName(cat?.name ?? "");
    const initial = categoryName ? categoryName.charAt(0).toUpperCase() : "₹";

    return (
        <div className="tx-item">
            <div
                className="tx-icon"
                style={{ background: cat ? `${cat.color}22` : "rgba(99,102,241,0.1)" }}
            >
                {initial}
            </div>
            <div className="tx-info">
                <div className="tx-description">
                    {tx.description || "No description"}
                </div>
                <div className="tx-meta">
                    {tx.date}
                    {categoryName && (
                        <span
                            className="badge"
                            style={{
                                marginLeft: 8,
                                background: `${cat.color}22`,
                                color: cat.color,
                            }}
                        >
                            {categoryName}
                        </span>
                    )}
                </div>
            </div>
            <div className={`tx-amount ${tx.type}`}>
                {tx.type === "expense" ? "-" : "+"}
                {fmt(tx.amount)}
            </div>
            {onEdit && (
                <button
                    className="btn btn-ghost"
                    onClick={() => onEdit(tx)}
                    style={{ padding: "4px 8px" }}
                >
                    <Pencil size={14} />
                </button>
            )}
            {onDelete && (
                <button
                    className="btn btn-danger"
                    onClick={() => onDelete(tx.id)}
                    style={{ padding: "4px 8px" }}
                >
                    <Trash2 size={14} />
                </button>
            )}
        </div>
    );
}
