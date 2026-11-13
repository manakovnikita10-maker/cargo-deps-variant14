"""Формирование DOT и отрисовка графа в SVG через Graphviz."""

import json
import shutil
import subprocess
import webbrowser


def dot_source(graph):
    """Преобразовать вершины и рёбра в исходный текст Graphviz."""
    lines = [
        "digraph dependencies {",
        "    rankdir=LR;",
        '    graph [pad=0.25, bgcolor="white"];',
        '    node [shape=box, style="rounded,filled", fontname="sans-serif",',
        '          fillcolor="#f1f5f9", color="#94a3b8"];',
        '    edge [color="#475569"];',
    ]
    root = next(iter(graph), None)
    root_style = ' [fillcolor="#dbeafe", color="#2563eb"]'
    for package in graph:
        label = json.dumps(package, ensure_ascii=False)
        style = root_style if package == root else ""
        lines.append(f"    {label}{style};")
    for package, dependencies in graph.items():
        parent = json.dumps(package, ensure_ascii=False)
        for dependency in dependencies:
            child = json.dumps(dependency, ensure_ascii=False)
            lines.append(f"    {parent} -> {child};")
    return "\n".join([*lines, "}", ""])


def render_graph(graph, directory, name):
    """Записать DOT и вызвать Graphviz для получения SVG."""
    executable = shutil.which("dot")
    if executable is None:
        raise ValueError("установите Graphviz и добавьте dot в PATH")
    directory.mkdir(parents=True, exist_ok=True)
    dot_file = directory / f"{name}.dot"
    svg_file = directory / f"{name}.svg"
    dot_file.write_text(dot_source(graph), encoding="utf-8")
    result = subprocess.run(
        [executable, "-Tsvg", str(dot_file), "-o", str(svg_file)],
        capture_output=True, text=True, check=False,
    )
    if result.returncode:
        raise ValueError(f"Graphviz: {result.stderr.strip()}")
    return dot_file, svg_file


def show_image(filename):
    """Открыть локальное изображение в стандартном браузере."""
    try:
        opened = webbrowser.open(filename.resolve().as_uri())
    except webbrowser.Error:
        opened = False
    if not opened:
        print(f"Откройте изображение: {filename.resolve()}")
