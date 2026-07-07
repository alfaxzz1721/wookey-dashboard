#!/usr/bin/env python3
"""
patch_theme.py
Tambah light/dark mode toggle ke semua file dashboard wookey.
Jalankan dari folder ~/wookey-dashboard/
"""

import os, re, sys
from pathlib import Path

DASHBOARD_DIR = Path.home() / "wookey-dashboard"

# ── CSS light mode variables ─────────────────────────────────
LIGHT_CSS = """
  /* ── Light Mode ──────────────────────────────────────────── */
  [data-theme="light"] {
    --bg:        #f0f2f8;
    --surface:   #ffffff;
    --surface2:  #f5f7fc;
    --border:    #e2e6f0;
    --text:      #1a1d2e;
    --muted:     #7b849a;
    --shopee:    #EE4D2D;
    --tiktok:    #ff0050;
    --green:     #059669;
    --red:       #dc2626;

    --c-gmv:      #d97706;
    --c-order:    #059669;
    --c-click:    #2563eb;
    --c-watch:    #7c3aed;
    --c-show:     #475569;
    --c-ctr:      #db2777;
    --c-ctor:     #0891b2;
    --c-aov:      #ea580c;
    --c-err:      #c026d3;
  }

  [data-theme="light"] body {
    background: var(--bg);
    color: var(--text);
  }

  [data-theme="light"] .chart-compare-summary .chart-summary-pill {
    background: #eef0f8;
  }

  [data-theme="light"] .compare-diff-tooltip {
    background: #ffffff;
    border-color: var(--border);
    color: var(--text);
    box-shadow: 0 4px 16px rgba(0,0,0,.12);
  }
  [data-theme="light"] .compare-diff-tooltip::after {
    border-top-color: #ffffff;
  }

  [data-theme="light"] .compare-info-popup {
    background: #ffffff;
    box-shadow: 0 4px 16px rgba(0,0,0,.12);
  }

  /* Theme toggle button */
  .theme-toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 9px 12px;
    border-radius: 7px;
    border: none;
    background: transparent;
    color: var(--muted);
    font-size: 13px;
    font-weight: 500;
    font-family: 'Inter', sans-serif;
    cursor: pointer;
    transition: all .15s;
    text-align: left;
  }
  .theme-toggle:hover {
    background: var(--surface2);
    color: var(--text);
  }
  .theme-toggle-track {
    width: 32px;
    height: 18px;
    border-radius: 9px;
    background: var(--border);
    position: relative;
    flex-shrink: 0;
    transition: background .2s;
    margin-left: auto;
  }
  .theme-toggle-track.on {
    background: #f59e0b;
  }
  .theme-toggle-thumb {
    position: absolute;
    top: 2px;
    left: 2px;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: white;
    transition: transform .2s;
    box-shadow: 0 1px 3px rgba(0,0,0,.2);
  }
  .theme-toggle-track.on .theme-toggle-thumb {
    transform: translateX(14px);
  }
"""

# ── JS untuk theme toggle ────────────────────────────────────
THEME_JS = """
// ── Theme Toggle (Light / Dark) ──────────────────────────────
function initTheme() {
  const saved = localStorage.getItem('wookey-theme') || 'dark';
  applyTheme(saved);
}
function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('wookey-theme', theme);
  const track = document.getElementById('theme-track');
  const icon  = document.getElementById('theme-icon');
  const label = document.getElementById('theme-label');
  if (!track) return;
  if (theme === 'light') {
    track.classList.add('on');
    if (icon)  icon.textContent  = '☀️';
    if (label) label.textContent = 'Mode Cerah';
  } else {
    track.classList.remove('on');
    if (icon)  icon.textContent  = '🌙';
    if (label) label.textContent = 'Mode Gelap';
  }
}
function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'dark';
  applyTheme(current === 'dark' ? 'light' : 'dark');
}
initTheme();
"""

# ── Tombol theme di sidebar ───────────────────────────────────
THEME_BUTTON_HTML = """      <div style="padding:0 12px 8px;">
        <button class="theme-toggle" onclick="toggleTheme()" title="Toggle tema cerah/gelap">
          <span id="theme-icon">🌙</span>
          <span id="theme-label">Mode Gelap</span>
          <div class="theme-toggle-track" id="theme-track">
            <div class="theme-toggle-thumb"></div>
          </div>
        </button>
      </div>"""

def patch_file(filepath: Path) -> bool:
    content = filepath.read_text(encoding='utf-8')
    original = content
    changed = False

    # 1. Tambah light mode CSS sebelum penutup </style> pertama
    if '[data-theme="light"]' not in content:
        content = content.replace('</style>', LIGHT_CSS + '\n</style>', 1)
        changed = True
        print(f"  ✓ Light CSS ditambahkan")

    # 2. Tambah theme JS sebelum penutup </script> terakhir
    if 'initTheme()' not in content:
        # Cari </script> terakhir dan tambahkan sebelumnya
        last_script_close = content.rfind('</script>')
        if last_script_close != -1:
            content = content[:last_script_close] + THEME_JS + '\n' + content[last_script_close:]
            changed = True
            print(f"  ✓ Theme JS ditambahkan")

    # 3. Tambah tombol theme di sidebar (sebelum penutup </aside> atau sebelum "margin-top:auto")
    if 'theme-toggle' not in content:
        # Cari posisi yang tepat: sebelum div margin-top:auto atau sebelum </aside>
        if 'margin-top:auto' in content:
            content = content.replace(
                '<div style="margin-top:auto;',
                THEME_BUTTON_HTML + '\n      <div style="margin-top:auto;',
                1
            )
            changed = True
            print(f"  ✓ Tombol theme ditambahkan ke sidebar")
        elif '</aside>' in content:
            content = content.replace('</aside>', THEME_BUTTON_HTML + '\n  </aside>', 1)
            changed = True
            print(f"  ✓ Tombol theme ditambahkan sebelum </aside>")

    if changed:
        filepath.write_text(content, encoding='utf-8')
        return True
    else:
        print(f"  ⏭ Sudah ada theme toggle, skip")
        return False

def main():
    html_files = list(DASHBOARD_DIR.glob("*.html"))
    if not html_files:
        print(f"❌ Tidak ada file HTML di {DASHBOARD_DIR}")
        sys.exit(1)

    print(f"📁 Dashboard: {DASHBOARD_DIR}")
    print(f"📄 Total file: {len(html_files)}\n")

    patched = 0
    for f in sorted(html_files):
        print(f"── {f.name}")
        if patch_file(f):
            patched += 1
        print()

    print(f"✅ Selesai — {patched}/{len(html_files)} file diupdate")
    print(f"\nSelanjutnya:")
    print(f"  cd ~/wookey-dashboard")
    print(f"  git add -A")
    print(f'  git commit -m "feat: tambah light/dark mode toggle di semua halaman"')
    print(f"  git push")

if __name__ == '__main__':
    main()
