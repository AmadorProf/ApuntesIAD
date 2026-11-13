#!/usr/bin/env python3
"""Add prev/next navigation slide to all UD presentations."""
import re
from pathlib import Path

REPO = Path(__file__).parent.parent

MODULES = [
    "CFS1_Gestion-de-datos-y-entrenamiento-IA/MP01_Procesamiento-Datos",
    "CFS1_Gestion-de-datos-y-entrenamiento-IA/MP02_Entrenamiento-Modelos",
    "CFS1_Gestion-de-datos-y-entrenamiento-IA/MP03_Desarrollo-Componentes-ML",
    "CFS1_Gestion-de-datos-y-entrenamiento-IA/MP04_Soluciones-LLM",
    "CFS2_Instalacion-despliegue-y-explotacion-de-sistemas-de-IA/MP01_Implementacion-Sistemas-IA",
    "CFS2_Instalacion-despliegue-y-explotacion-de-sistemas-de-IA/MP02_Despliegue-Sistemas-IA",
    "CFS2_Instalacion-despliegue-y-explotacion-de-sistemas-de-IA/MP03_Explotacion-Servicios-Datos",
    "CFS2_Instalacion-despliegue-y-explotacion-de-sistemas-de-IA/MP04_Infraestructura-LLM",
]

NAV_MARKER = "<!-- nav-slide -->"


def get_ud_title(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^# (UD\d+ · .+)$", text, re.MULTILINE)
    if m:
        return m.group(1)
    return path.parent.name


def shorten(title: str, max_len: int = 35) -> str:
    if len(title) <= max_len:
        return title
    return title[:max_len].rstrip() + "…"


def process_module(module_rel: str):
    module_path = REPO / module_rel
    ud_dirs = sorted(
        [d for d in module_path.iterdir() if d.is_dir() and re.match(r"UD\d+", d.name)],
        key=lambda d: int(re.search(r"UD(\d+)", d.name).group(1)),
    )

    titles = {}
    for ud_dir in ud_dirs:
        index = ud_dir / "index.md"
        if index.exists():
            titles[ud_dir.name] = get_ud_title(index)

    for i, ud_dir in enumerate(ud_dirs):
        index = ud_dir / "index.md"
        if not index.exists():
            continue
        content = index.read_text(encoding="utf-8")
        if NAV_MARKER in content:
            print(f"  SKIP {ud_dir.name} (ya tiene navegación)")
            continue

        prev_name = ud_dirs[i - 1].name if i > 0 else None
        next_name = ud_dirs[i + 1].name if i < len(ud_dirs) - 1 else None

        links = []
        if prev_name:
            t = shorten(titles.get(prev_name, prev_name))
            links.append(f"[← {t}](../{prev_name}/)")
        links.append("[Volver al módulo](../)")
        if next_name:
            t = shorten(titles.get(next_name, next_name))
            links.append(f"[{t} →](../{next_name}/)")

        nav_slide = f"\n\n---\n\n{NAV_MARKER}\n\n## Navegación\n\n" + " &nbsp;·&nbsp; ".join(links) + "\n"
        index.write_text(content + nav_slide, encoding="utf-8")
        print(f"  OK  {ud_dir.name}")


for module in MODULES:
    print(f"\n{module}")
    process_module(module)

print("\nListo.")
