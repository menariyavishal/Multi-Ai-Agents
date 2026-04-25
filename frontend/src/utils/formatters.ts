import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Utility to merge tailwind classes efficiently using clsx and tailwind-merge
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Truncate long text
 */
export function truncate(text: string, length = 100): string {
  if (!text) return '';
  return text.length > length ? text.substring(0, length) + '...' : text;
}
