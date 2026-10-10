#!/usr/bin/env python3
"""
İdrakin Deli Gömleği — Çevrimdışı E-Kitap Derleyici v2.0
-------------------------------------------------------
Tüm temel dokümanları (README, MANIFESTO, ACTION_PLAN, LITERATURE, CONTRIBUTING)
bağımsız, sıfır ağ bağımlılıklı, yüksek tipografiye sahip tek bir çevrimdışı
HTML e-kitap dosyasına derler.
"""

import os
import re
import datetime

def markdown_to_rich_html(md_text):
    # Process fenced code blocks first
    def code_block_sub(match):
        lang = match.group(1) or ""
        code = match.group(2).replace("<", "&lt;").replace(">", "&gt;")
        if lang == "mermaid":
            return f'<div class="mermaid-box"><pre class="mermaid-raw">{code}</pre></div>'
        return f'<pre class="code-block"><code class="language-{lang}">{code}</code></pre>'

    md_text = re.sub(r'```([a-zA-Z0-9_-]*)\n(.*?)```', code_block_sub, md_text, flags=re.DOTALL)

    # Process Tables
    def table_sub(match):
        lines = match.group(0).strip().split('\n')
        if len(lines) < 2:
            return match.group(0)
        
        headers = [c.strip() for c in lines[0].strip('|').split('|')]
        # line 1 is separator | :--- | :--- |
        rows = []
        for line in lines[2:]:
            cols = [c.strip() for c in line.strip('|').split('|')]
            rows.append(cols)

        html = ['<div class="table-container"><table>']
        html.append('<thead><tr>')
        for h in headers:
            html.append(f'<th>{h}</th>')
        html.append('</tr></thead><tbody>')
        for r in rows:
            html.append('<tr>')
            for c in r:
                html.append(f'<td>{c}</td>')
            html.append('</tr>')
        html.append('</tbody></table></div>')
        return '\n'.join(html)

    md_text = re.sub(r'(\|[^\n]+\|\n\|[\s:-|]+\|\n(?:\|[^\n]+\|\n?)+)', table_sub, md_text)

    # Headings
    md_text = re.sub(r'^### (.*)$', r'<h3 id="\1">\1</h3>', md_text, flags=re.M)
    md_text = re.sub(r'^## (.*)$', r'<h2 id="\1">\1</h2>', md_text, flags=re.M)
    md_text = re.sub(r'^# (.*)$', r'<h1 id="\1">\1</h1>', md_text, flags=re.M)

    # Bold & Italic
    md_text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', md_text)
    md_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', md_text)
    md_text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', md_text)

    # Blockquotes
    md_text = re.sub(r'^> (.*)$', r'<blockquote>\1</blockquote>', md_text, flags=re.M)

    # Checkboxes & Lists
    md_text = re.sub(r'^- \[x\] (.*)$', r'<li class="checked"><input type="checkbox" checked disabled> \1</li>', md_text, flags=re.M)
    md_text = re.sub(r'^- \[ \] (.*)$', r'<li class="unchecked"><input type="checkbox" disabled> \1</li>', md_text, flags=re.M)
    md_text = re.sub(r'^\* (.*)$', r'<li>\1</li>', md_text, flags=re.M)
    md_text = re.sub(r'^- (.*)$', r'<li>\1</li>', md_text, flags=re.M)

    # Horizontal Rule
    md_text = re.sub(r'^---$', r'<hr class="divider">', md_text, flags=re.M)

    # Paragraph formatting
    paragraphs = md_text.split('\n\n')
    formatted = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if any(p.startswith(tag) for tag in ['<h', '<blockquote', '<li', '<table', '<div', '<pre', '<hr', '<p', '<img', '<input']):
            formatted.append(p)
        else:
            formatted.append(f'<p>{p}</p>')

    return '\n'.join(formatted)

def build_offline_book():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    readme_path = os.path.join(base_dir, 'README.md')
    manifesto_path = os.path.join(base_dir, 'MANIFESTO.md')
    action_path = os.path.join(base_dir, 'ACTION_PLAN.md')
    lit_path = os.path.join(base_dir, 'LITERATURE.md')
    contrib_path = os.path.join(base_dir, 'CONTRIBUTING.md')

    documents = [
        (readme_path, "📖 Ana Eser & Ansiklopedik Metin"),
        (manifesto_path, "📜 10 Temel İlke ve Bildirge"),
        (action_path, "🛠️ Otonom Eylem Planı"),
        (lit_path, "📚 Felsefi ve Sosyolojik Düşünce Atlası"),
        (contrib_path, "🤝 Ahilik ve Katkı Rehberi")
    ]

    toc_items = []
    merged_content = ""
    for idx, (path, title) in enumerate(documents, 1):
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                raw_text = f.read()
                section_id = f"dokuman-bolum-{idx}"
                toc_items.append(f'<li><a href="#{section_id}">{title}</a></li>')
                merged_content += f'\n\n<section id="{section_id}" class="book-chapter">\n\n'
                merged_content += f'# {title}\n\n'
                merged_content += raw_text
                merged_content += '\n\n</section>\n\n'

    html_body = markdown_to_rich_html(merged_content)
    today = datetime.date.today().strftime("%d.%m.%Y")

    html_template = f"""<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>İdrakin Deli Gömleği — Tam Çevrimdışı Külliyat</title>
  <style>
    :root {{
      --bg: #090c10;
      --card-bg: #111620;
      --text: #e6edf3;
      --text-muted: #8b949e;
      --accent: #e63946;
      --border: #21262d;
    }}
    body {{
      font-family: 'Newsreader', Georgia, serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.85;
      font-size: 1.15rem;
      max-width: 900px;
      margin: 0 auto;
      padding: 40px 24px;
    }}
    h1, h2, h3, h4 {{
      font-family: 'Cinzel', 'Times New Roman', serif;
      color: var(--text);
      line-height: 1.3;
    }}
    h1 {{
      font-size: 2.2rem;
      color: var(--accent);
      border-bottom: 2px solid var(--border);
      padding-bottom: 12px;
      margin-top: 2.5rem;
    }}
    h2 {{
      font-size: 1.6rem;
      margin-top: 2rem;
      border-bottom: 1px solid var(--border);
      padding-bottom: 8px;
    }}
    h3 {{
      font-size: 1.3rem;
      margin-top: 1.5rem;
      color: #f87171;
    }}
    p {{
      margin: 1.2rem 0;
    }}
    blockquote {{
      border-left: 4px solid var(--accent);
      background: rgba(230, 57, 70, 0.08);
      padding: 16px 20px;
      margin: 1.5rem 0;
      border-radius: 0 8px 8px 0;
      font-style: italic;
    }}
    .table-container {{
      overflow-x: auto;
      margin: 1.5rem 0;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--card-bg);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 0.95rem;
    }}
    th, td {{
      padding: 12px 16px;
      border-bottom: 1px solid var(--border);
      text-align: left;
    }}
    th {{
      background: rgba(0, 0, 0, 0.4);
      color: var(--accent);
      font-weight: 700;
    }}
    tr:hover {{
      background: rgba(255, 255, 255, 0.02);
    }}
    pre.code-block, pre.mermaid-raw {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      overflow-x: auto;
      font-family: 'JetBrains Mono', Consolas, monospace;
      font-size: 0.9rem;
      color: #93c5fd;
    }}
    li {{
      margin: 0.5rem 0;
    }}
    li.checked {{
      color: #34d399;
    }}
    .divider {{
      border: 0;
      border-top: 1px solid var(--border);
      margin: 2.5rem 0;
    }}
    .book-toc {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      padding: 24px;
      border-radius: 12px;
      margin-bottom: 3rem;
    }}
    .book-toc h2 {{
      margin-top: 0;
      font-size: 1.3rem;
      border: none;
    }}
    .book-toc ul {{
      list-style: none;
      padding-left: 0;
    }}
    .book-toc li {{
      margin: 0.6rem 0;
    }}
    .book-toc a {{
      color: var(--accent);
      text-decoration: none;
      font-weight: 600;
    }}
    .book-toc a:hover {{
      text-decoration: underline;
    }}
    .book-header {{
      text-align: center;
      margin-bottom: 3rem;
      padding-bottom: 2rem;
      border-bottom: 2px solid var(--border);
    }}
    @media print {{
      body {{ background: #fff !important; color: #000 !important; font-size: 11pt !important; }}
      .book-toc {{ page-break-after: always; background: #fff !important; border: 1px solid #ccc !important; }}
      .book-chapter {{ page-break-before: always; }}
      h1, h2, h3 {{ color: #000 !important; }}
      blockquote {{ background: #f5f5f5 !important; border-left-color: #333 !important; color: #111 !important; }}
      table, th, td {{ border-color: #ccc !important; }}
      th {{ background: #eee !important; color: #000 !important; }}
    }}
  </style>
</head>
<body>
  <div class="book-header">
    <div style="font-family: sans-serif; font-size: 0.85rem; color: #8b949e; letter-spacing: 2px; text-transform: uppercase;">Milli İcazetsiz Düşünce ve Otonom Üretim Külliyatı</div>
    <h1 style="border: none; margin: 12px 0 6px 0; font-size: 2.6rem;">İDRAKİN DELİ GÖMLEĞİ</h1>
    <div style="font-style: italic; color: #8b949e; font-size: 1.25rem;">Üniversite, Tecessüsün Katli ve Teslimiyet Senedi</div>
    <div style="font-family: monospace; font-size: 0.8rem; margin-top: 15px; color: #8b949e;">Derleme Tarihi: {today} • CC BY-NC-SA 4.0</div>
  </div>

  <div class="book-toc">
    <h2>📚 Külliyat İçindekiler</h2>
    <ul>
      {''.join(toc_items)}
    </ul>
  </div>

  {html_body}

  <footer style="margin-top: 4rem; padding-top: 2rem; border-top: 1px solid var(--border); text-align: center; font-size: 0.85rem; font-family: monospace; color: var(--text-muted);">
    İdrakin Deli Gömleği — Çevrimdışı E-Kitap Edisyonu • Tamamı Özgür & Açık Kaynak
  </footer>
</body>
</html>"""

    out_file = os.path.join(base_dir, 'dist', 'idrakin-deli-gomlegi-kitap.html')
    os.makedirs(os.path.join(base_dir, 'dist'), exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"[OK] Çevrimdışı zengin külliyat e-kitabı oluşturuldu: {out_file}")
    return out_file

if __name__ == '__main__':
    build_offline_book()
