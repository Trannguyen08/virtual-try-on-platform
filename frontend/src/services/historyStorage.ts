import { TryOnHistoryItem } from '../data/mockHistory';

const STORAGE_KEY = 'vfit_tryon_history';
export const HISTORY_RETENTION_MS = 5 * 60 * 1000;
let legacyStorageCleared = false;

function isUnexpired(item: unknown, now: number): item is TryOnHistoryItem {
  if (!item || typeof item !== 'object') return false;
  const candidate = item as TryOnHistoryItem;
  return typeof candidate.id === 'string'
    && typeof candidate.productName === 'string'
    && typeof candidate.category === 'string'
    && Number.isFinite(candidate.timestamp)
    && now - candidate.timestamp < HISTORY_RETENTION_MS
    && candidate.timestamp <= now;
}

export const historyStorage = {
  getHistory(): TryOnHistoryItem[] {
    try {
      if (!legacyStorageCleared) {
        try { localStorage.removeItem(STORAGE_KEY); } catch { /* Remove legacy persistent history when available. */ }
        legacyStorageCleared = true;
      }
      const stored = sessionStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed)) {
          const now = Date.now();
          const active = parsed.filter((item) => isUnexpired(item, now));
          if (active.length !== parsed.length) {
            try { sessionStorage.setItem(STORAGE_KEY, JSON.stringify(active)); } catch { /* Keep the in-memory result for this read. */ }
          }
          return active.sort((a, b) => b.timestamp - a.timestamp);
        }
      }
    } catch {
      // Treat unreadable or unavailable local storage as an empty history.
    }
    return [];
  },

  saveItem(item: TryOnHistoryItem): TryOnHistoryItem[] {
    try {
      const current = this.getHistory();
      // Prepend the new item
      const updated = [item, ...current.filter((h) => h.id !== item.id)];
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      window.setTimeout(() => { this.getHistory(); }, HISTORY_RETENTION_MS);
      return updated;
    } catch {
      return [];
    }
  },

  deleteItem(id: string): TryOnHistoryItem[] {
    try {
      const current = this.getHistory();
      const updated = current.filter((h) => h.id !== id);
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
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
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      return updated;
    } catch {
      return [];
    }
  },

  clearAll(): void {
    try {
      sessionStorage.removeItem(STORAGE_KEY);
    } catch {
      // ignore
    }
  },
};
