import { atom, computed } from 'nanostores';
import type { User } from '../types';

// Auth Store
interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export const authStore = atom<AuthState>({
  user: null,
  token: typeof window !== 'undefined' ? sessionStorage.getItem('access_token') : null,
  refreshToken: typeof window !== 'undefined' ? sessionStorage.getItem('refresh_token') : null,
  isAuthenticated: typeof window !== 'undefined' ? !!sessionStorage.getItem('access_token') : false,
  isLoading: false,
});

export const isAuthenticated = computed(authStore, (state) => state.isAuthenticated);

export function setAuth(user: User, token: string, refreshToken: string) {
  sessionStorage.setItem('access_token', token);
  sessionStorage.setItem('refresh_token', refreshToken);
  authStore.set({
    user,
    token,
    refreshToken,
    isAuthenticated: true,
    isLoading: false,
  });
}

export function clearAuth() {
  sessionStorage.removeItem('access_token');
  sessionStorage.removeItem('refresh_token');
  authStore.set({
    user: null,
    token: null,
    refreshToken: null,
    isAuthenticated: false,
    isLoading: false,
  });
}

export function setUser(user: User) {
  authStore.set({ ...authStore.get(), user });
}

// Toast Store
export interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
}

export const toasts = atom<Toast[]>([]);

let toastCounter = 0;

export function showToast(message: string, type: Toast['type'] = 'info', duration = 4000) {
  const id = `toast-${++toastCounter}`;
  const toast: Toast = { id, message, type, duration };
  toasts.set([...toasts.get(), toast]);

  if (duration > 0) {
    setTimeout(() => {
      removeToast(id);
    }, duration);
  }

  // Also show in DOM
  renderToast(toast);
}

export function removeToast(id: string) {
  toasts.set(toasts.get().filter((t) => t.id !== id));
  const el = document.getElementById(id);
  if (el) {
    el.style.opacity = '0';
    el.style.transform = 'translateX(100%)';
    setTimeout(() => el.remove(), 300);
  }
}

function renderToast(toast: Toast) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const colorMap = {
    success: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
    error: 'bg-red-500/10 border-red-500/30 text-red-400',
    warning: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
    info: 'bg-indigo-500/10 border-indigo-500/30 text-indigo-400',
  };

  const iconMap = {
    success: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>',
    error: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>',
    warning: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>',
    info: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>',
  };

  const el = document.createElement('div');
  el.id = toast.id;
  el.className = `flex items-center gap-3 px-4 py-3 rounded-lg border ${colorMap[toast.type]} transition-all duration-300 translate-x-full opacity-0`;
  el.innerHTML = `
    <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">${iconMap[toast.type]}</svg>
    <span class="text-sm font-medium">${toast.message}</span>
    <button onclick="removeToast('${toast.id}')" class="ml-auto opacity-60 hover:opacity-100">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
    </button>
  `;

  container.appendChild(el);
  requestAnimationFrame(() => {
    el.style.opacity = '1';
    el.style.transform = 'translateX(0)';
  });
}

// UI Store
interface UIState {
  sidebarOpen: boolean;
  theme: 'dark' | 'light' | 'system';
  searchQuery: string;
}

export const uiStore = atom<UIState>({
  sidebarOpen: false,
  theme: 'dark',
  searchQuery: '',
});

export function toggleSidebar() {
  const current = uiStore.get();
  uiStore.set({ ...current, sidebarOpen: !current.sidebarOpen });
}

export function setSearchQuery(query: string) {
  uiStore.set({ ...uiStore.get(), searchQuery: query });
}

// Notification Store
interface NotificationState {
  unreadCount: number;
  hasNew: boolean;
}

export const notificationStore = atom<NotificationState>({
  unreadCount: 0,
  hasNew: false,
});

export function setUnreadCount(count: number) {
  notificationStore.set({ unreadCount: count, hasNew: count > 0 });
}

// Make removeToast available globally
if (typeof window !== 'undefined') {
  (window as any).removeToast = removeToast;
}
