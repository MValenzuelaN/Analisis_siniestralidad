import importlib
import os
import re
import subprocess
from pathlib import Path
import shutil
from datetime import datetime
from importlib import metadata
import sys
import time



#---------------------------------
# BOOTSTRAP DE DEPENDENCIAS
# ---------------------------------
# requirements.txt resuelto junto a este archivo (funciona aunque se ejecute
# desde otra carpeta).
REQUIREMENTS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "requirements.txt"
)

# Extrae el nombre del paquete al inicio de una línea de requirements.
_REQ_NOMBRE_RE = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")


def _leer_requirements(path):
    """Devuelve [(linea_completa, nombre_paquete)] ignorando comentarios, vacíos y flags."""
    reqs = []
    if not os.path.isfile(path):
        return reqs
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            linea = raw.split("#", 1)[0].strip()  # quitar comentarios en línea
            if not linea or linea.startswith("-"):  # ignorar vacíos y flags (-r, -e)
                continue
            m = _REQ_NOMBRE_RE.match(linea)
            if m:
                reqs.append((linea, m.group(1)))
    return reqs


def _esta_instalado(nombre_paquete):
    """True si la distribución está instalada (búsqueda por nombre PyPI, no por nombre de import)."""
    try:
        metadata.distribution(nombre_paquete)
        return True
    except metadata.PackageNotFoundError:
        return False


def asegurar_dependencias(path=REQUIREMENTS_FILE):
    """Instala, con el MISMO intérprete que ejecuta este script, solo las dependencias que falten."""
    reqs = _leer_requirements(path)
    if not reqs:
        print(
            f"[DEPS] No se encontró requirements en: {path} (se omite la verificación)"
        )
        return

    faltantes = [linea for (linea, nombre) in reqs if not _esta_instalado(nombre)]

    if not faltantes:
        print(f"[DEPS] Todas las dependencias presentes ({len(reqs)} verificadas).")
        return

    print(f"[DEPS] Faltan {len(faltantes)} dependencia(s): {', '.join(faltantes)}")
    print("[DEPS] Instalando...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *faltantes])
    except subprocess.CalledProcessError as e:
        print(f"[DEPS][ERROR] Falló la instalación (pip código {e.returncode}).")
        raise
    importlib.invalidate_caches()  # necesario para poder importar lo recién instalado
    print("[DEPS] Instalación finalizada.")


# Verificar/instalar ANTES de importar librerías de terceros (que pueden faltar):
asegurar_dependencias()


#-------------------------------------------------------------------#
#####################################################################
#            Generación de informe técnico y entregables            #
#####################################################################
#-------------------------------------------------------------------#

# import subprocess
# import shutil
# import time
# from pathlib import Path
# from datetime import datetime

# ---------------------------
# Esperar a que aparezca archivo
# ---------------------------
def esperar_archivo(path, timeout=5):
    inicio = time.time()
    while time.time() < inicio + timeout:
        if path.exists():
            return True
        time.sleep(0.5)
    return False

# ---------------------------
# Ejecutar archivo QMD
# ---------------------------
def ejecutar_qmd(nombre_archivo):
    carpeta_script = Path(__file__).resolve().parent
    ruta_archivo = carpeta_script / nombre_archivo

    print(f"Buscando {nombre_archivo}...")

    if not ruta_archivo.exists():
        print(f"[ERROR] El archivo '{nombre_archivo}' no existe.")
        return

    print(f"{nombre_archivo} encontrado")

    try:
        resultado = subprocess.run(
            ["quarto", "render", str(ruta_archivo)],
            stderr=subprocess.PIPE,
            text=True,
            cwd=ruta_archivo.parent
        )

        if resultado.returncode == 0:
            print("[OK] Renderizado correcto")

            # Construir ruta REAL del HTML
            html_path = ruta_archivo.with_suffix(".html")

            print("Esperando HTML generado...")

            if not esperar_archivo(html_path):
                print("[ERROR] El HTML no apareció después de renderizar")
                print("Archivos encontrados en carpeta:")
                for f in ruta_archivo.parent.glob("*.html"):
                    print(" -", f.name)
                return

            mover_html(html_path)

        else:
            print("[ERROR] al ejecutar el archivo:")
            print(resultado.stderr)

    except FileNotFoundError:
        print("[ERROR] Quarto no está instalado o no está en el PATH.")
        print("Instálalo desde: https://quarto.org")


# ---------------------------
# Mover y renombrar HTML
# ---------------------------
def mover_html(origen):
    origen = Path(origen)

    #print("Origen real:", origen)
    print("Existe HTML generado:", origen.exists())

    if not origen.exists():
        print(f"[ERROR] No se encontró el archivo HTML.")
        return

    # generar fecha actual
    fecha = datetime.now().strftime("%Y-%m-%d")

    # separar nombre y extensión
    nombre_base = origen.stem
    extension = origen.suffix

    # nuevo nombre con fecha
    nuevo_nombre = f"{nombre_base}_{fecha}{extension}"

    # definir raíz del proyecto (sube un nivel desde Plantillas)
    PROJECT_ROOT = origen.parent.parent

    destino_dir = PROJECT_ROOT / "Salidas"
    destino = destino_dir / nuevo_nombre

    print("Destino:", destino)

    # crear carpeta si no existe
    destino_dir.mkdir(parents=True, exist_ok=True)

    # mover archivo
    shutil.move(str(origen), str(destino))

    print(f"[OK] Archivo movido como: {nuevo_nombre}")


# ---------------------------
# USO
# ---------------------------
if __name__ == "__main__":
    ejecutar_qmd("Informe_siniestralidad.qmd")
