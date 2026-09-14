##################################################
#
# chat2pdf
#
# Parses json files from a full ChatGTP Backup 
# into LaTeX .tex format, and then generate PDFs
#
# 2026 (c) Quanta Sciences | Rama Hoetzlein
# https://github.com/quantasci
# MIT License
#
##################################################

import json
import os
import re
import unicodedata
import shutil
import subprocess
import tempfile
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Source & Output Paths
#
heading_path = "heading.tex"

if (len(sys.argv)!=3):
    print ("\nchat2gpt")
    print ("2026 (c) Quanta Sciences | Rama Hoetzlein. MIT License")
    print ("Usage: chat2gpt {input_folder} {output_folder}\n")
    print ("--> Please specify input folder of an unzipped ChatGTP Backup, and output folder for destination tex/pdf files.\n")
    sys.exit(1)

input_dir = sys.argv[1]
output_dir = sys.argv[2]

if not os.path.isdir(input_dir):
    print(f"ERROR: Input directory does not exist: {input_dir}")
    sys.exit(1)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

with open(heading_path, "r", encoding="utf-8") as f:
     heading = f.read()

import os
import re

def update_unicode_inventory(text, master_file):
    """Find all non-ASCII Unicode characters in text and append to master file"""
    # Find every non-ASCII character.
    unicode_chars = sorted(
        set(
            ch
            for ch in text
            if ord(ch) > 127
            and not ch.isspace()
        ),
        key=ord
    )
    if not unicode_chars:
        return
    master_path = Path(master_file)
    existing = set()
    if master_path.exists():
        with open(master_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                # Character is everything before the first tab.
                char = line.split("\t", 1)[0]
                existing.add(char)
    # Append only new characters.
    new_chars = [
        ch
        for ch in unicode_chars
        if ch not in existing
    ]
    if not new_chars:
        return
    with open(master_path, "a", encoding="utf-8") as f:
        for ch in new_chars:
            codepoint = f"U+{ord(ch):04X}"
            name = unicodedata.name(ch, "UNKNOWN")
            f.write(f"{ch}\n")

def safe_filename(name):
    """Make a string safe to use as a filename."""
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name[:150] or "Untitled"

def clean_chatgpt(text):
    """Remove ChatGPT content markers"""
    def remove_private_use(ch):
        code = ord(ch)
        return not (
            0xE000 <= code <= 0xF8FF or
            0xF0000 <= code <= 0xFFFFD or
            0x100000 <= code <= 0x10FFFD
        )
    text = re.sub(r'', '', text, flags=re.DOTALL)
    text = ''.join(
        ch for ch in text
        if remove_private_use(ch)
    )
    """Replace genui"""
    text = re.sub(r'genui\{.*?\}+\s*', '', text, flags=re.DOTALL)       
    return text

def unicode_math_to_latex(text):
    """
    Convert common Unicode mathematical symbols to LaTeX.

    Symbols are wrapped in $...$ when they represent mathematical
    notation occurring in ordinary text.
    """
    replacements = {
        # Greek letters
        "α": r"$\alpha$",
        "β": r"$\beta$",
        "γ": r"$\gamma$",
        "δ": r"$\delta$",
        "ε": r"$\epsilon$",
        "ϵ": r"$\varepsilon$",
        "ζ": r"$\zeta$",
        "η": r"$\eta$",
        "θ": r"$\theta$",
        "ϑ": r"$\vartheta$",
        "ι": r"$\iota$",
        "κ": r"$\kappa$",
        "λ": r"$\lambda$",
        "μ": r"$\mu$",
        "ν": r"$\nu$",
        "ξ": r"$\xi$",
        "π": r"$\pi$",
        "ϖ": r"$\varpi$",
        "ρ": r"$\rho$",
        "ϱ": r"$\varrho$",
        "σ": r"$\sigma$",
        "ς": r"$\varsigma$",
        "τ": r"$\tau$",
        "υ": r"$\upsilon$",
        "φ": r"$\phi$",
        "ϕ": r"$\varphi$",
        "χ": r"$\chi$",
        "ψ": r"$\psi$",
        "ω": r"$\omega$",

        # Capital Greek
        "Γ": r"$\Gamma$",
        "Δ": r"$\Delta$",
        "Θ": r"$\Theta$",
        "Λ": r"$\Lambda$",
        "Ξ": r"$\Xi$",
        "Π": r"$\Pi$",
        "Σ": r"$\Sigma$",
        "Υ": r"$\Upsilon$",
        "Φ": r"$\Phi$",
        "Ψ": r"$\Psi$",
        "Ω": r"$\Omega$",

        # Mathematical operators
        "⊕": r"$\oplus$",
        "⊗": r"$\otimes$",
        "⊙": r"$\odot$",
        "⊖": r"$\ominus$",
        "⊘": r"$\oslash$",
        "∪": r"$\cup$",
        "∩": r"$\cap$",
        "∈": r"$\in$",
        "∉": r"$\notin$",
        "⊂": r"$\subset$",
        "⊆": r"$\subseteq$",
        "⊃": r"$\supset$",
        "⊇": r"$\supseteq$",

        # Relations
        "≤": r"$\leq$",
        "≥": r"$\geq$",
        "≠": r"$\neq$",
        "≈": r"$\approx$",
        "≃": r"$\simeq$",
        "≅": r"$\cong$",
        "≡": r"$\equiv$",
        "∼": r"$\sim$",
        "∝": r"$\propto$",

        # Arrows
        "→": r"$\rightarrow$",
        "←": r"$\leftarrow$",
        "↔": r"$\leftrightarrow$",
        "⇒": r"$\Rightarrow$",
        "⇐": r"$\Leftarrow$",
        "⇔": r"$\Leftrightarrow$",
        "↦": r"$\mapsto$",
        "↑": r"$\uparrow$",
        "↓": r"$\downarrow$",

        # Other common mathematical symbols
        "∞": r"$\infty$",
        "∂": r"$\partial$",
        "∇": r"$\nabla$",
        "√": r"$\sqrt{}$",
        "∫": r"$\int$",
        "∑": r"$\sum$",
        "∏": r"$\prod$",
        "∀": r"$\forall$",
        "∃": r"$\exists$",
        "∅": r"$\emptyset$",
        "ℝ": r"$\mathbb{R}$",
        "ℕ": r"$\mathbb{N}$",
        "ℤ": r"$\mathbb{Z}$",
        "ℚ": r"$\mathbb{Q}$",
        "ℂ": r"$\mathbb{C}$",

        # Math-like punctuation
        "·": r"$\cdot$",
        "×": r"$\times$",
        "÷": r"$\div$",
        "±": r"$\pm$",
        "∓": r"$\mp$",
        "₀": r"$0$",
        "₁": r"$1$",
        "₂": r"$2$",
        "₃": r"$3$",
        "₄": r"$4$",
        "₅": r"$5$",
        "₆": r"$6$",
        "₇": r"$7$",
        "₈": r"$8$",
        "₉": r"$9$",
        "₊": r"$+$",
        "₋": r"$-$",
        "₌": r"$=$",
        "₍": r"$($",
        "₎": r"$)$",
        "ₐ": r"$a$",
        "ₑ": r"$e$",
        "ₕ": r"$h$",
        "ᵢ": r"$i$",
        "ⱼ": r"$j$",
        "ₖ": r"$k$",
        "ₗ": r"$l$",
        "ₘ": r"$m$",
        "ₙ": r"$n$",
        "ₒ": r"$o$",
        "ₚ": r"$p$",
        "ᵣ": r"$r$",
        "ₛ": r"$s$",
        "ₜ": r"$t$",
        "ᵤ": r"$u$",
        "ᵥ": r"$v$",
        "ₓ": r"$x$",
        "❌":r"\texttimes",
        "✅":r"\checkmark",
        "✓":r"$\checkmark$",
        "✔":r"$\checkmark$",
        "✗":r"$\times$",
        "✘":r"$\times$",
    }
    #== First replace math with latex math
    for unicode_char, latex in replacements.items():
                 text = text.replace(unicode_char, latex)
        #== Replace any remaining unicode
    unicode_chars = sorted(
        set(
          ch
          for ch in text
          if ord(ch) > 127
          and not ch.isspace()
        ),
        key=ord
    )
    replacements = {}
    for ch in unicode_chars:        
        normalized = unicodedata.normalize("NFKD", ch)
        ascii_text = "".join(
            c for c in normalized
            if ord(c) < 128
            and not unicodedata.combining(c)
        )
        replacements[ch] = ascii_text
    text = "".join(replacements.get(ch, ch) for ch in text)
    return text

def escape_latex_text(content):
    protected = []
    def protect(match):
        protected.append(match.group(0))
        return f'\x00{len(protected) - 1}\x00'
    content = re.sub(r'\\(?:[#$%&_{}^~]|textbackslash\{\})', protect, content)
    content = re.sub(r'\\', r'\textbackslash{}', content)
    content = re.sub(r'([#$%&_{}])', r'\\\1', content)
    content = re.sub(r'\^', r'\textasciicircum{}', content)
    content = re.sub(r'~', r'\textasciitilde{}', content)
    return re.sub(
        r'\x00(\d+)\x00',
        lambda m: protected[int(m.group(1))],
        content
    )

def markdown_to_latex(text):
    """Convert basic Markdown to LaTeX while preserving existing LaTeX math."""
    # =========================================================
    # 00. Convert code
    def convert_code(match):
        code = match.group(1)
        code = code.replace('\\', r'\textbackslash{}')
        code = code.replace('_', r'\_')
        code = code.replace('%', r'\%')
        code = code.replace('&', r'\&')
        code = code.replace('#', r'\#')
        return rf'\texttt{{{code}}}'
    text = re.sub(
        r'`([^`\n]+)`',
        convert_code,
        text
    )
    # =========================================================
    # 0. Remove ChatGPT citaton artifacts
    text = re.sub(r'', '', text, flags=re.DOTALL) 
    text = re.sub(r'\bcite(?:turn\d+(?:search|news|reddit|image|product|business|youtube)\d+)+\b',
        '', 
        text )

    text = ''.join(  
        ch for ch in text 
        if not ( 0xE000 <= ord(ch) <= 0xF8FF or 0xF0000 <= ord(ch) <= 0xFFFFD or 0x100000 <= ord(ch) <= 0x10FFFD ) 
    )
    # =========================================================
    # 1. Fix escaped comparison operators in ordinary text
    text = text.replace(r'\<', '<')
    text = text.replace(r'\>', '>')
    # =========================================================
    # 2. Protect existing math / LaTeX blocks
    math_blocks = []

    def protect_math(match):
        math_blocks.append(match.group(0))
        return f"@@MATH{len(math_blocks) - 1}@@"

    # Display math: $$ ... $$
    text = re.sub(
        r'\$\$.*?\$\$',
        protect_math,
        text,
        flags=re.DOTALL
    )
    # Display math: \[ ... \]
    text = re.sub(
        r'\\\[.*?\\\]',
        protect_math,
        text,
        flags=re.DOTALL
    )
    # LaTeX math environments
    text = re.sub(
        r'\\begin\{(?:align\*?|equation\*?|gather\*?|'
        r'multline\*?|split|cases|array|matrix|pmatrix|bmatrix|'
        r'vmatrix|Vmatrix)\}.*?'
        r'\\end\{(?:align\*?|equation\*?|gather\*?|'
        r'multline\*?|split|cases|array|matrix|pmatrix|bmatrix|'
        r'vmatrix|Vmatrix)\}',
        protect_math,
        text,
        flags=re.DOTALL
    )
    # Inline math: \( ... \)
    text = re.sub(
        r'\\\(.*?\\\)',
        protect_math,
        text,
        flags=re.DOTALL
    )
    # Inline math: $ ... $
    text = re.sub(
        r'\$(?!\$).*?(?<!\$)\$',
        protect_math,
        text
    )
    # =========================================================
    # 3. Convert Markdown headings
    def convert_heading(match):
        hashes = match.group(1)
        title = match.group(2).strip()
        title = re.sub(
            r'\*\*([^*\n]+?)\*\*',
            lambda m: r'\textbf{' + m.group(1) + '}',
            title
        )
        title = re.sub(
            r'(?<!\*)\*([^*\n]+?)\*(?!\*)',
            lambda m: r'\textit{' + m.group(1) + '}',
            title
        )
        level = len(hashes)
        if level == 1:
            return r'\section*{' + title + '}'
        elif level == 2:
            return r'\subsection*{' + title + '}'
        else:
           return r'\subsubsection*{' + title + '}'

    text = re.sub(
        r'^(#{1,3})\s+(.+)$',
        convert_heading,
        text,
        flags=re.MULTILINE
    )
    # =========================================================
    # 4. Convert Markdown bold
    def convert_bold(match):
        content = match.group(1)
        if content.count('{') != content.count('}'):
            return match.group(0)
        return r'\textbf{' + escape_latex_text(content) + '}'
    text = re.sub(
        r'\*\*(.+?)\*\*',
        convert_bold,
        text
    )
    # =========================================================
    # 5. Convert Markdown italic
    def convert_italic(match):
        content = match.group(1)
        if content.count('{') != content.count('}'):
            return match.group(0)
        return r'\textit{' + escape_latex_text(content) + '}'
    text = re.sub(
        r'(?<!\*)\*([^*\n]+?)\*(?!\*)',
        convert_italic,
        text
    )
    # =========================================================
    # 6. Escape ordinary text
    text = re.sub(r'(?<!\\)&', r'\&', text)
    text = re.sub(r'(?<!\\)#', r'\#', text)
    text = re.sub(r'(?<!\\)_', r'\_', text)
    text = re.sub(r'(?<!\\)%', r'\%', text)

    # =========================================================
    # 7. Restore protected math
    for i, math in enumerate(math_blocks):
        text = text.replace(
            f"@@MATH{i}@@",
            math
        )

    return text

def tex_to_pdf(tex_path):
    tex_path = os.path.abspath(tex_path)
    output_dir = os.path.dirname(tex_path)
    basename = os.path.splitext(os.path.basename(tex_path))[0]
    tmpdir = os.path.join(output_dir, "temp")
    os.makedirs(tmpdir, exist_ok=True)
    tmp_tex = os.path.join(tmpdir, os.path.basename(tex_path))
    shutil.copy2(tex_path, tmp_tex)

    final_pdf = os.path.join(output_dir, basename + ".pdf")
    if os.path.exists(final_pdf):
        os.remove(final_pdf)

    try:
        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-output-directory", tmpdir,
                tmp_tex,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, 
            cwd=tmpdir,
            text=True,
            timeout=20,
        )
    except subprocess.TimeoutExpired:
        print(f"*** Failed (timeout): {tex_path}")
        return None

    pdf_path = os.path.join(tmpdir, basename + ".pdf")

    if result.returncode != 0 or not os.path.exists(pdf_path):
        print(f"*** Failed: {tex_path}")
        return None

    shutil.copy2(pdf_path, final_pdf)
    shutil.rmtree(tmpdir, ignore_errors=True)
    return final_pdf


def extract_messages(mapping):
    children = defaultdict(list)
    root_id = None
    for node_id, node in mapping.items():
        parent_id = node.get("parent")
        if parent_id is None:
            root_id = node_id
        else:
            children[parent_id].append(node_id)
    for parent_id in children:
        children[parent_id].sort(
            key=lambda node_id: mapping[node_id].get("create_time") or 0
        )
    messages = []

    def walk(node_id):
        node = mapping.get(node_id)
        if node is None:
            return
        message = node.get("message")
        if message:
            role = message.get("author", {}).get("role")
            content = message.get("content") or {}
            parts = content.get("parts") or []
            text = "\n".join(
                str(part)
                for part in parts
                if isinstance(part, str)
            ).strip()
            if role in ("user", "assistant") and text:
                messages.append((role, text))
        for child_id in children.get(node_id, []):
            walk(child_id)
    if root_id is not None:
        walk(root_id)
    return messages


def extract_conversations(input_file, output_dir):
    """
    Extract all conversations from a ChatGPT JSON export.
    All conversations are written directly into output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)

    with open(input_file, "r", encoding="utf-8") as f:
        conversations = json.load(f)

    update_unicode_inventory(
        json.dumps(conversations, ensure_ascii=False),
        "unicode_chars.txt"
    )
    extracted_count = 0

    for index, conversation in enumerate(conversations, start=1):

        # Skip anything that isn't a JSON object/dictionary
        if not hasattr(conversation, "get"):
            print(f"  Skipping entry {index}: not a JSON object")
            continue

        title = conversation.get("title", "Untitled")

        # Convert create_time to a readable date
        create_time = conversation.get("create_time")

        if create_time is not None:
            try:
                date = datetime.fromtimestamp(
                    create_time
                ).strftime("%Y-%m-%d")
            except (ValueError, TypeError, OSError):
                date = "Unknown-Date"
        else:
            date = "Unknown-Date"
        filename = (
            f"{date} - "
            f"{safe_filename(title)}.tex"
        )
        output_path = os.path.join(output_dir, filename)
        mapping = conversation.get("mapping", {})

        # Extract the ChatGPT message tree from .json in correct ordering
        messages = extract_messages(mapping)

        # Write the conversation
        with open(output_path, "w", encoding="utf-8") as out:

            out.write(heading)
            out.write(f"\\section*{{{title}}}\n\n")
            out.write(f"Created: {date}\n\n")

            for role, text in messages:

                if role == "user":
                    out.write("\\begin{userbox}\n\\textbf{User:}\n\n")
                else:
                    out.write("ChatGPT:\n\n")

                # Preserve Markdown/LaTeX
                text = clean_chatgpt(text)
                text = unicode_math_to_latex(text)
                text = markdown_to_latex(text)
                out.write( text )
                out.write("\n\n")
                out.write("---\n\n")

                if role == "user": 
                    out.write("\\end{userbox}\n\n")

            out.write("\\end{document}")

        pdf_path = tex_to_pdf(output_path)

        extracted_count += 1
        print(f"  Created: {filename}")

    print(f"  {extracted_count} conversations extracted.")


def main():

    os.makedirs(output_dir, exist_ok=True)

    # Find every JSON file in the input directory
    json_files = sorted(
        filename
        for filename in os.listdir(input_dir)
        if filename.lower().endswith(".json")
    )

    print(f"Found {len(json_files)} JSON files.")

    for json_filename in json_files:

        input_file = os.path.join(
            input_dir,
            json_filename
        )

        print(f"\nProcessing: {json_filename}")

        extract_conversations(
            input_file,
            output_dir
        )

    print("\nAll files processed.")


if __name__ == "__main__":
    main()