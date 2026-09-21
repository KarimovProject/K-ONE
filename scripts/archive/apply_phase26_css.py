import os
from pathlib import Path

def update_css():
    base_dir = Path("c:/IEMS/static/css")
    
    # 1. Update tokens.css
    tokens_file = base_dir / "tokens.css"
    content = tokens_file.read_text(encoding="utf-8")
    content = content.replace("--weight-black:          var(--weight-extrabold);", "--weight-black:          700;")
    tokens_file.write_text(content, encoding="utf-8")

    # 2. Update components.css
    comp_file = base_dir / "components.css"
    content = comp_file.read_text(encoding="utf-8")
    
    if ".premium-segmented-nav" not in content:
        segmented_css = """
/* ==========================================================================
   PREMIUM SEGMENTED NAV (Phase 26)
   ========================================================================== */
.premium-segmented-nav {
  display: inline-flex;
  align-items: center;
  background: var(--color-surface-1);
  padding: 4px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-subtle);
}

.premium-segment-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: var(--radius-md);
  font-family: var(--font-sans);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  color: var(--color-text-secondary);
  text-decoration: none;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all var(--duration-fast);
}

.premium-segment-btn:hover {
  color: var(--color-text-title);
  background: rgba(15, 23, 42, 0.04);
}

.premium-segment-btn.active {
  background: var(--color-ink);
  color: var(--color-text-inverse) !important;
  font-weight: var(--weight-semibold);
  box-shadow: 0 2px 4px rgba(10, 17, 40, 0.12);
}

.premium-segment-btn.active svg {
  color: var(--color-sky-light);
}
"""
        content = content.replace("/* --------------------------------------------------------------------------\n   5. COMMAND FILTER BAR", segmented_css + "\n/* --------------------------------------------------------------------------\n   5. COMMAND FILTER BAR")
        
    comp_file.write_text(content, encoding="utf-8")
    print("Updated CSS components")

if __name__ == "__main__":
    update_css()
