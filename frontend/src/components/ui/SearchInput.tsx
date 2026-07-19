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

  return (
    <div className={cn("relative w-full", className)}>
      <Search
        className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted"
        aria-hidden="true"
      />
      <input
        type="search"
        role="searchbox"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder}
        className="h-11 w-full rounded-lg border border-surface-700 bg-surface-800 pl-9 pr-9 text-base text-text-high placeholder:text-text-muted transition-all duration-200 hover:border-primary/50 focus:outline-none focus:ring-2 focus:ring-primary-glow focus:ring-offset-2 focus:ring-offset-surface-900 [&::-webkit-search-cancel-button]:hidden"
      />
      {value && (
        <button
          type="button"
          onClick={() => setValue("")}
          aria-label="Clear search"
          className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted transition-colors hover:text-text-high"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}

export default SearchInput;
