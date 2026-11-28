
import { useState } from "react";

type Theme = "light" | "dark" | "system";

interface HeaderProps {
  theme: Theme;
  onThemeChange: (theme: Theme) => void;
}

export function Header({ theme, onThemeChange }: HeaderProps) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="top-header">
      <a className="brand" href="#" aria-label="Noteway home">
        <span className="brand-icon" aria-hidden="true">
          <svg viewBox="0 0 48 48" fill="none">
            <path
              d="M39.5 5.5C22 6.5 10 16 8 29.5c-.6 4.2.4 8.3 2.5 11.5C15 29 24 19.5 36 12.5 27 21 18 31 13 42c11.5-4.5 19-13 23-25.5 1.5-4.5 2.5-8 3.5-11Z"
              fill="currentColor"
            />
            <path
              d="M9 42c7-10 14-17 24-24"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </span>
        <span>Noteway</span>
      </a>

      <div className={`theme-menu ${menuOpen ? "open" : ""}`}>
        <button
          className="theme-toggle"
          type="button"
          onClick={() => setMenuOpen((open) => !open)}
          aria-label="Choose theme"
          aria-haspopup="menu"
          aria-expanded={menuOpen}
          title="Choose theme"
        >
          {theme === "light" ? (
            // Sun icon
            <svg viewBox="0 0 24 24" fill="none">
              <circle
                cx="12"
                cy="12"
                r="4"
                stroke="currentColor"
                strokeWidth="1.8"
              />
              <path
                d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
              />
            </svg>
          ) : theme === "dark" ? (
            // Moon icon
            <svg viewBox="0 0 24 24" fill="none">
              <path
                d="M20.2 15.1A8.5 8.5 0 0 1 8.9 3.8 8.5 8.5 0 1 0 20.2 15.1Z"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinejoin="round"
              />
            </svg>
          ) : (
            // System / monitor icon
            <svg viewBox="0 0 24 24" fill="none">
              <rect
                x="3"
                y="4"
                width="18"
                height="14"
                rx="2"
                stroke="currentColor"
                strokeWidth="1.8"
              />
              <path
                d="M8 21h8m-4-3v3"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
              />
            </svg>
          )}
        </button>

        {menuOpen && (
          <div className="theme-dropdown" role="menu">
            <button
              type="button"
              role="menuitem"
              className={`theme-option ${theme === "light" ? "active" : ""}`}
              onClick={() => {
                onThemeChange("light");
                setMenuOpen(false);
              }}
            >
              <span className="theme-option-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none">
                  <circle
                    cx="12"
                    cy="12"
                    r="4"
                    stroke="currentColor"
                    strokeWidth="1.8"
                  />
                  <path
                    d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                  />
                </svg>
              </span>
              Light
              {theme === "light" && <span className="theme-check">✓</span>}
            </button>

            <button
              type="button"
              role="menuitem"
              className={`theme-option ${theme === "dark" ? "active" : ""}`}
              onClick={() => {
                onThemeChange("dark");
                setMenuOpen(false);
              }}
            >
              <span className="theme-option-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none">
                  <path
                    d="M20.2 15.1A8.5 8.5 0 0 1 8.9 3.8 8.5 8.5 0 1-A20.2 15.1Z"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinejoin="round"
                  />
                </svg>
              </span>
              Dark
              {theme === "dark" && <span className="theme-check">✓</span>}
            </button>

            <button
              type="button"
              role="menuitem"
              className={`theme-option ${theme === "system" ? "active" : ""}`}
              onClick={() => {
                onThemeChange("system");
                setMenuOpen(false);
              }}
            >
              <span className="theme-option-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none">
                  <rect
                    x="3"
                    y="4"
                    width="18"
                    height="14"
                    rx="2"
                    stroke="currentColor"
                    strokeWidth="1.8"
                  />
                  <path
                    d="M8 21h8m-4-3v3"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                  />
                </svg>
              </span>
              System
              {theme === "system" && <span className="theme-check">✓</span>}
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
