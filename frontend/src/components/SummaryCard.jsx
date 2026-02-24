export default function SummaryCard({ label, value, icon, variant = "" }) {
    const formatted =
        typeof value === "number"
            ? new Intl.NumberFormat("en-IN", {
                style: "currency",
                currency: "INR",
                maximumFractionDigits: 0,
            }).format(Math.abs(value))
            : value;

    return (
        <div className="summary-card">
            <div
                className="summary-card-icon"
                style={{ background: "rgba(99,102,241,0.15)" }}
            >
                {icon}
            </div>
            <div className="summary-card-label">{label}</div>
            <div className={`summary-card-value ${variant}`}>{formatted}</div>
        </div>
    );
}
