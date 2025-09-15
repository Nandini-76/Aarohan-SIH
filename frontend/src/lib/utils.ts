import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export function formatTime(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatPercentage(value: number, decimals = 1): string {
  return `${value.toFixed(decimals)}%`;
}

export function getRiskColor(phase: string): string {
  switch (phase) {
    case "Green": return "text-success";
    case "Yellow": return "text-warning";
    case "Orange": return "text-orange";
    case "Red": return "text-destructive";
    default: return "text-muted-foreground";
  }
}

export function getRiskBgColor(phase: string): string {
  switch (phase) {
    case "Green": return "bg-success/10";
    case "Yellow": return "bg-warning/10";
    case "Orange": return "bg-orange/10";
    case "Red": return "bg-destructive/10";
    default: return "bg-muted/10";
  }
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}