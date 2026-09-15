import React, { useEffect, useRef, useState } from "react";

function matches(value, query) {
  const normalizedValue = value.toLowerCase();
  const normalizedQuery = query.trim().toLowerCase();
  return !normalizedQuery || normalizedValue.includes(normalizedQuery);
}

export default function LocationAutocomplete({
  value,
  onChange,
  onSelect,
  suggestions = [],
  placeholder,
  disabled = false,
  noResultsText = "No results found",
  className = "text-input",
  id,
  "aria-label": ariaLabel,
}) {
  const containerRef = useRef(null);
  const inputRef = useRef(null);
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const filtered = suggestions.filter((item) => matches(item, value)).slice(0, 8);

  useEffect(() => {
    const handleOutsideClick = (event) => {
      if (!containerRef.current?.contains(event.target)) setOpen(false);
    };
    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  useEffect(() => setActiveIndex(-1), [value, suggestions]);

  const selectValue = (nextValue) => {
    onSelect?.(nextValue);
    onChange(nextValue);
    setOpen(false);
    setActiveIndex(-1);
  };

  const handleKeyDown = (event) => {
    if (disabled) return;
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setOpen(true);
      setActiveIndex((index) => Math.min(index + 1, filtered.length - 1));
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setActiveIndex((index) => Math.max(index - 1, 0));
    } else if (event.key === "Enter" && open && activeIndex >= 0) {
      event.preventDefault();
      selectValue(filtered[activeIndex]);
    } else if (event.key === "Escape") {
      setOpen(false);
      setActiveIndex(-1);
    }
  };

  const showNoResults = open && value.trim() && filtered.length === 0;
  const listId = `${id || "location"}-suggestions`;

  return (
    <div className="location-autocomplete" ref={containerRef}>
      <input
        ref={inputRef}
        id={id}
        className={className}
        value={value}
        onChange={(event) => {
          onChange(event.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        autoComplete="off"
        role="combobox"
        aria-label={ariaLabel || placeholder}
        aria-expanded={open}
        aria-controls={listId}
        aria-activedescendant={activeIndex >= 0 ? `${listId}-${activeIndex}` : undefined}
      />

      {open && !disabled && (filtered.length > 0 || showNoResults) && (
        <div className="location-suggestions" id={listId} role="listbox">
          {filtered.length > 0 ? filtered.map((item, index) => (
            <button
              type="button"
              key={item}
              id={`${listId}-${index}`}
              className={index === activeIndex ? "location-suggestion active" : "location-suggestion"}
              role="option"
              aria-selected={index === activeIndex}
              onMouseDown={(event) => event.preventDefault()}
              onClick={() => selectValue(item)}
              onMouseEnter={() => setActiveIndex(index)}
            >
              {item}
            </button>
          )) : (
            <div className="location-no-results" role="status">{noResultsText}</div>
          )}
        </div>
      )}
    </div>
  );
}
