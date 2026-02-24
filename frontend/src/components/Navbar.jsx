import { NavLink } from "react-router-dom";
import { LayoutDashboard, ArrowLeftRight, Wallet, LineChart } from "lucide-react";

const links = [
    { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { to: "/transactions", label: "Transactions", icon: ArrowLeftRight },
    { to: "/budgets", label: "Budgets", icon: Wallet },
    { to: "/analytics", label: "Analytics", icon: LineChart },
];

export default function Navbar() {
    return (
        <nav className="navbar">
            <div className="navbar-logo">
                <span>💸</span>
                <span>SpendSmart</span>
            </div>
            {links.map(({ to, label, icon: Icon }) => (
                <NavLink
                    key={to}
                    to={to}
                    className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
                >
                    <Icon size={16} strokeWidth={2} />
                    {label}
                </NavLink>
            ))}
        </nav>
    );
}
