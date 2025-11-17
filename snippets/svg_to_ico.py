#!/usr/bin/env python3
"""Converte arquivos SVG (ex.: `favicon.svg`, `placeholder.svg`) para `.ico`.

O script procura recursivamente na pasta `assets` (ou no caminho passado via --assets)
arquivos chamados `favicon.svg` e `placeholder.svg` (case-insensitive) e gera arquivos
`.ico` ao lado do SVG encontrado.

Requisitos:
  pip install cairosvg pillow

Uso:
  python snippets/svg_to_ico.py --assets ./assets [--yes] [--verbose]

Por padrão o script não sobrescreve arquivos `.ico` existentes a menos que
você passe --yes.
"""
from __future__ import annotations

import argparse
import os
from io import BytesIO
from typing import List

TARGET_NAMES = {"favicon.svg", "placeholder.svg"}


def find_svgs(root: str, names: set) -> List[str]:
    matches: List[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower() in names:
                matches.append(os.path.join(dirpath, fn))
    return matches


def ensure_deps():
    missing = []
    try:
        import cairosvg  # noqa: F401
    except Exception:
        missing.append("cairosvg")
    try:
        from PIL import Image  # noqa: F401
    except Exception:
        missing.append("Pillow")

    if missing:
        pkg_list = " ".join(missing)
        raise RuntimeError(
            f"Dependências ausentes: {', '.join(missing)}. Instale com: pip install {pkg_list}"
        )


def svg_to_ico(svg_path: str, overwrite: bool = False, verbose: bool = False) -> bool:
    """Converte o `svg_path` para um `.ico` do mesmo nome (na mesma pasta).

    Retorna True se um arquivo foi criado/atualizado, False caso contrário.
    """
    from PIL import Image
    import cairosvg

    out_path = os.path.splitext(svg_path)[0] + ".ico"
    if os.path.exists(out_path) and not overwrite:
        if verbose:
            print(f"Pulando (existe): {out_path}")
        return False

    # Renderizar em PNG em alta resolução e deixar Pillow gerar os tamanhos menores
    max_size = 256
    with open(svg_path, "rb") as fh:
        svg_bytes = fh.read()

    png_bytes = cairosvg.svg2png(bytestring=svg_bytes, output_width=max_size, output_height=max_size)
    img = Image.open(BytesIO(png_bytes)).convert("RGBA")

    # Alguns ICO preferem múltiplos tamanhos; Pillow aceita `sizes` ao salvar.
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    try:
        img.save(out_path, format="ICO", sizes=sizes)
    except Exception:
        # fallback: salvar apenas o tamanho atual
        img.save(out_path, format="ICO")

    if verbose:
        print(f"Gerado: {out_path}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Converte favicon.svg/placeholder.svg para .ico")
    parser.add_argument("--assets", "-a", default="assets", help="Pasta raiz de assets (padrão: assets)")
    parser.add_argument("--yes", "-y", action="store_true", help="Permite sobrescrever arquivos .ico existentes")
    parser.add_argument("--verbose", "-v", action="store_true", help="Saída detalhada")
    args = parser.parse_args()

    assets_root = os.path.abspath(args.assets)
    if not os.path.isdir(assets_root):
        print(f"Pasta de assets não encontrada: {assets_root}")
        return 2

    try:
        ensure_deps()
    except RuntimeError as e:
        print(str(e))
        return 3

    names = {n.lower() for n in TARGET_NAMES}
    svgs = find_svgs(assets_root, names)
    if not svgs:
        print("Nenhum favicon.svg ou placeholder.svg encontrado em:", assets_root)
        return 0

    created = 0
    for s in svgs:
        if svg_to_ico(s, overwrite=args.yes, verbose=args.verbose):
            created += 1

    print(f"Processados: {len(svgs)} — ICOs gerados/atualizados: {created}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
