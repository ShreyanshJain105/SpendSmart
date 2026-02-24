/**
 * AppContext — global state shared across pages.
 *
 * Kept intentionally narrow: categories (cached on mount) and the
 * currently selected month filter.  Anything that is local to a single
 * page stays in that page's useState.
 */
import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { getCategories } from "../api/categories";

const AppContext = createContext(null);

export function AppProvider({ children }) {
    const [categories, setCategories] = useState([]);
    const [activeMonth, setActiveMonth] = useState(() => {
        const now = new Date();
        return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
    });

    const refreshCategories = useCallback(async () => {
        try {
            const data = await getCategories();
            setCategories(data);
        } catch {
            // Categories are non-critical; silent fail is acceptable here
        }
    }, []);

    useEffect(() => {
        refreshCategories();
    }, [refreshCategories]);

    return (
        <AppContext.Provider
            value={{ categories, refreshCategories, activeMonth, setActiveMonth }}
        >
            {children}
        </AppContext.Provider>
    );
}

export const useApp = () => {
    const ctx = useContext(AppContext);
    if (!ctx) throw new Error("useApp must be used within AppProvider");
    return ctx;
};
