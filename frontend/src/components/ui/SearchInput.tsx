"use client";

import { useEffect, useRef, useState } from "react";
import { Search, X } from "lucide-react";
import { cn } from "@/lib/utils";

export interface SearchInputProps {
  /** Called with the query after the debounce delay */
  onSearch: (query: string) => void;
  placeholder?: string;
  debounceMs?: number;
  className?: string;
  defaultValue?: string;
  /** "hero" renders the large glowing bar used on the dashboard */
  variant?: "default" | "hero";
}

/**
 * Debounced search input with a leading search icon and clear button.
 */
export function SearchInput({
  onSearch,
  placeholder = "Search tools...",
  debounceMs = 300,
  className,
  defaultValue = "",
  variant = "default",
}: SearchInputProps) {
  const [value, setValue] = useState(defaultValue);
  const onSearchRef = useRef(onSearch);

  useEffect(() => {
    onSearchRef.current = onSearch;
  }, [onSearch]);

  useEffect(() => {
    const handle = setTimeout(() => onSearchRef.current(value), debounceMs);
    return () => clearTimeout(handle);
  }, [value, debounceMs]);

  const isHero = variant === "hero";

  return (
    <div className={cn("relative w-full", className)}>
      <Search
        className={cn(
          "pointer-events-none absolute top-1/2 -translate-y-1/2",
          isHero
            ? "left-5 h-5 w-5 text-accent"
            : "left-3 h-4 w-4 text-text-muted"
        )}
        aria-hidden="true"
      />
      <input
        type="search"
        role="searchbox"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder}
        className={cn(
          "w-full transition-all duration-200 focus:outline-none [&::-webkit-search-cancel-button]:hidden",
          isHero
            ? "h-14 rounded-2xl border border-primary/30 bg-white pl-13 pr-12 text-lg text-surface-900 shadow-[0_0_25px_rgba(163,177,138,0.35),0_0_50px_rgba(88,129,87,0.2)] placeholder:text-accent/70 focus:shadow-[0_0_30px_rgba(163,177,138,0.5),0_0_60px_rgba(88,129,87,0.3)]"
            : "h-11 rounded-lg border border-surface-700 bg-surface-800 pl-9 pr-9 text-base text-text-high placeholder:text-text-muted hover:border-primary/50 focus:ring-2 focus:ring-primary-glow focus:ring-offset-2 focus:ring-offset-surface-900"
        )}
      />
      {value && (
        <button
          type="button"
          onClick={() => setValue("")}
          aria-label="Clear search"
          className={cn(
            "absolute top-1/2 -translate-y-1/2 transition-colors",
            isHero
              ? "right-4 text-accent hover:text-surface-900"
              : "right-3 text-text-muted hover:text-text-high"
          )}
        >
          <X className={isHero ? "h-5 w-5" : "h-4 w-4"} />
        </button>
      )}
    </div>
  );
}

export default SearchInput;
