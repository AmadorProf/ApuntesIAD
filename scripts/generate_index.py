#!/usr/bin/env python3
"""Generate indice.html — global index of all UDs grouped by module."""
import re
from pathlib import Path

REPO = Path(__file__).parent.parent

MODULES = [
    {
        "cfs": "CFS1",
        "cfs_title": "CFS1 — Gestión de datos y entrenamiento IA (IAD)",
        "color": "#3b82f6",
        "bg": "#eff6ff",
        "dirs": [
            ("CFS1_Gestion-de-datos-y-entrenamiento-IA/MP01_Procesamiento-Datos", "MP01 · Procesamiento de datos para IA"),
            ("CFS1_Gestion-de-datos-y-entrenamiento-IA/MP02_Entrenamiento-Modelos", "MP02 · Entrenamiento de modelos de aprendizaje automático"),
            ("CFS1_Gestion-de-datos-y-entrenamiento-IA/MP03_Desarrollo-Componentes-ML", "MP03 · Desarrollo de componentes para sistemas de ML"),
            ("CFS1_Gestion-de-datos-y-entrenamiento-IA/MP04_Soluciones-LLM", "MP04 · Soluciones basadas en LLMs"),
        ],
    },
    {
        "cfs": "CFS2",
        "cfs_title": "CFS2 — Instalación, despliegue y explotación de sistemas de IA (IAD)",
        "color": "#10b981",
        "bg": "#ecfdf5",
        "dirs": [
            ("CFS2_Instalacion-despliegue-y-explotacion-de-sistemas-de-IA/MP01_Implementacion-Sistemas-IA", "MP01 · Implementación de sistemas de IA"),
            ("CFS2_Instalacion-despliegue-y-explotacion-de-sistemas-de-IA/MP02_Despliegue-Sistemas-IA", "MP02 · Despliegue de sistemas de IA"),
            ("CFS2_Instalacion-despliegue-y-explotacion-de-sistemas-de-IA/MP03_Explotacion-Servicios-Datos", "MP03 · Explotación de servicios de datos y analítica"),
            ("CFS2_Instalacion-despliegue-y-explotacion-de-sistemas-de-IA/MP04_Infraestructura-LLM", "MP04 · Infraestructura para la ejecución de LLMs"),
        ],
    },
]


def get_ud_title(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^# (UD\d+ · .+)$", text, re.MULTILINE)
    return m.group(1) if m else path.parent.name


def build_html() -> str:
    sections = []
    for cfs in MODULES:
        module_blocks = []
        for rel_dir, mp_title in cfs["dirs"]:
            mp_path = REPO / rel_dir
            ud_dirs = sorted(
                [d for d in mp_path.iterdir() if d.is_dir() and re.match(r"UD\d+", d.name)],
                key=lambda d: int(re.search(r"UD(\d+)", d.name).group(1)),
            )
            items = []
            for ud_dir in ud_dirs:
                index = ud_dir / "index.md"
                if index.exists():
                    title = get_ud_title(index)
                    href = f"./{rel_dir}/{ud_dir.name}/"
                    ud_num = re.search(r"UD(\d+)", ud_dir.name).group(1)
                    items.append(
                        f'<li><span class="ud-badge" style="background:{cfs["color"]}">UD{ud_num}</span>'
                        f'<a href="{href}">{title}</a></li>'
                    )
            module_blocks.append(
                f'<div class="module"><h3>{mp_title}</h3><ul>{"".join(items)}</ul></div>'
            )
        sections.append(
            f'<section class="cfs-section" style="border-color:{cfs["color"]};background:{cfs["bg"]}">'
            f'<h2 style="color:{cfs["color"]}">{cfs["cfs_title"]}</h2>'
            f'{"".join(module_blocks)}'
            f"</section>"
        )

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Índice de unidades didácticas | ApuntesIAD</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f8fafc; color: #1e293b; line-height: 1.6; }}
  header {{ background: #1e3a5f; color: white; padding: 24px 32px; }}
  header h1 {{ font-size: 1.6em; font-weight: 700; }}
  header p {{ font-size: 0.9em; color: #94a3b8; margin-top: 4px; }}
  nav.breadcrumb {{ padding: 12px 32px; background: white; border-bottom: 1px solid #e2e8f0; font-size: 0.85em; }}
  nav.breadcrumb a {{ color: #3b82f6; text-decoration: none; }}
  main {{ max-width: 960px; margin: 32px auto; padding: 0 24px 64px; }}
  .cfs-section {{ border-left: 4px solid; border-radius: 8px; padding: 24px 28px; margin-bottom: 32px; }}
  .cfs-section h2 {{ font-size: 1.1em; font-weight: 700; margin-bottom: 20px; }}
  .module {{ margin-bottom: 20px; }}
  .module h3 {{ font-size: 0.95em; font-weight: 600; color: #374151; margin-bottom: 10px; border-bottom: 1px solid #e5e7eb; padding-bottom: 4px; }}
  ul {{ list-style: none; display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 8px; }}
  li {{ display: flex; align-items: flex-start; gap: 10px; }}
  .ud-badge {{ color: white; font-size: 0.72em; font-weight: 700; padding: 2px 8px; border-radius: 12px; white-space: nowrap; margin-top: 3px; flex-shrink: 0; }}
  a {{ color: #1e3a5f; text-decoration: none; font-size: 0.88em; }}
  a:hover {{ text-decoration: underline; }}
  footer {{ text-align: center; font-size: 0.8em; color: #94a3b8; padding: 24px; border-top: 1px solid #e2e8f0; }}
</style>
</head>
<body>
<header>
  <h1>ApuntesIAD — Índice de unidades didácticas</h1>
  <p>Inteligencia Artificial y Datos · Nivel 3</p>
</header>
<nav class="breadcrumb">
  <a href="./">Inicio</a> › Índice completo
</nav>
<main>
{"".join(sections)}
</main>
<footer>CFS IAD · Formación Profesional Especializada · Nivel 3</footer>
</body>
</html>
"""


output = REPO / "indice.html"
output.write_text(build_html(), encoding="utf-8")
print(f"Generado: {output}")
