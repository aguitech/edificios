# 🏢 Edificio — Blender 3D Procedural

Edificio moderno de 5 pisos generado proceduralmente con **Blender 5.2 LTS** + `bpy` (headless).

Inspirado en arquitectura contemporánea con **voladizos en zigzag**, balcones de cristal y fachada curva en planta baja.

![Render principal](imagenes/render_ultimo.png)

## 🎨 Características

- **5 pisos** de 3.2m con voladizos alternados en X/Y (zigzag)
- **Balcones de cristal** y barandillas por nivel
- **Planta baja** con fachada curva (restaurante) — 16 segmentos cilíndricos
- **Pérgola metálica** en esquina superior
- **Mobiliario urbano**: acera, calle, líneas peatonales, edificio vecino
- **87 objetos** generados proceduralmente
- Materiales: cristal, concreto, madera, metal, asfalto
- Sky procedural (Hosek-Wilkie) + sol + fill light

## 🚀 Generar el edificio

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background --python build_edificio.py
```

Salida:
- `edificio.blend` — archivo Blender nativo
- `imagenes/render_YYYYMMDD_HHMMSS.png` — preview PNG

## 📁 Estructura

```
edificio/
├── README.md
├── build_edificio.py         # Generador procedural
├── edificio.blend             # Archivo Blender (87 objetos)
├── imagenes/                  # Historial de renders
│   ├── render_20260115_153022.png
│   ├── render_20260115_154512.png
│   └── render_ultimo.png      # Symlink al más reciente
└── .gitignore
```

## 🔧 Stack

- **Blender 5.2.0 LTS**
- **bpy** (Python API)
- **EEVEE** engine para preview rápido
- Sin dependencias externas

## 📐 Arquitectura

| Elemento | Dimensión |
|---|---|
| Pisos | 5 (PB + 4) |
| Altura por piso | 3.2 m |
| Ancho × Profundo | 22 × 16 m |
| Voladizo | 1.8 m |
| Altura total | ~16.4 m |

## 📜 Licencia

MIT
