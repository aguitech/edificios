# 🏢 Edificios — Blender 3D Procedural

Colección de edificios generados proceduralmente con **Blender 5.2 LTS** + `bpy` (headless).

## 🏗️ Edificios disponibles

| # | Nombre | Tipo | Pisos | Altura | Estilo |
|---|---|---|---|---|---|
| 1 | `edificio1.blend` | Comercial / oficinas | 5 | ~16 m | Balcones perimetrales de 2m, fachada curva en PB, pérgola |
| 2 | `edificio2.blend` | Residencial de lujo | 25 | 75 m | Fachada cristal negro + ventanas iluminadas, golden hour |

## 📁 Estructura del repo

```
edificio/
├── README.md                    ← este archivo
├── .gitignore
└── edificios/
    ├── edificio1/               ← comercial / oficinas
    │   ├── build.py             ← script generador
    │   ├── edificio1.blend      ← archivo Blender
    │   └── imagenes/            ← historial de renders + render_ultimo.png
    └── edificio2/               ← torre residencial golden hour
        ├── build.py
        ├── edificio2.blend
        └── imagenes/
```

## 🚀 Generar un edificio

```bash
cd edificios/edificio1
/Applications/Blender.app/Contents/MacOS/Blender --background --python build.py
```

Salida:
- `edificioN.blend` — archivo Blender
- `imagenes/render_YYYYMMDD_HHMMSS.png` — render nuevo con timestamp
- `imagenes/render_ultimo.png` — symlink al más reciente

## 📤 Deploy (build + commit + push)

```bash
./deploy.sh edificio2 "feat: torre golden hour 25 pisos"
```

Hace:
1. Corre el `build.py` del edificio
2. Genera el render nuevo
3. Commit con el mensaje
4. Push a `origin/main`

## 🎨 Stack

- **Blender 5.2.0 LTS** headless
- **Python 3.13** (embebido en Blender)
- **bpy** para geometría procedural
- **EEVEE** para render rápido
- **Sintetizadores nativos** para texturas (sin dependencias externas)

## 📜 Licencia

MIT
