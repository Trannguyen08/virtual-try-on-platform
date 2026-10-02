import { INITIAL_MOCK_HISTORY, TryOnHistoryItem } from '../data/mockHistory';

const STORAGE_KEY = 'vfit_tryon_history';

export const historyStorage = {
  getHistory(): TryOnHistoryItem[] {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed) && parsed.length > 0) {
          return parsed;
        }
      }
    } catch {
      // ignore JSON parse or localStorage failure
    }
    // Return default initial list if empty
    return INITIAL_MOCK_HISTORY;
  },

  saveItem(item: TryOnHistoryItem): TryOnHistoryItem[] {
    try {
      const current = this.getHistory();
      // Prepend the new item
      const updated = [item, ...current.filter((h) => h.id !== item.id)];
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      return updated;
    } catch {
      return INITIAL_MOCK_HISTORY;
    }
  },

  deleteItem(id: string): TryOnHistoryItem[] {
    try {
      const current = this.getHistory();
      const updated = current.filter((h) => h.id !== id);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      return updated;
    } catch {
      return [];
    }
  },

  toggleCart(id: string): TryOnHistoryItem[] {
    try {
      const current = this.getHistory();
      const updated = current.map((h) =>
        h.id === id ? { ...h, inCart: !h.inCart } : h
      );
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      return updated;
    } catch {
      return [];
    }
  },

  clearAll(): void {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      // ignore
    }
  },
};
