import os, sys, json, math, traceback, platform, ast, operator, random, datetime, threading, zipfile, shutil, time
from pathlib import Path
import pygame

# ============================================================
# KINETIX 1.0 - main.py
# ============================================================
# Pygame-only mobile OS simulation. No real clock is read.

ANCHO, ALTO, FPS = 400, 600, 60
FONDO=(28,30,38); FONDO_APP=(36,38,48); BARRA=(15,17,24)
GRIS=(150,155,165); GRIS_CLARO=(215,218,225); GRIS_OSCURO=(60,64,76)
AZUL=(52,152,219); VERDE=(46,204,113); ROJO=(231,76,60); NARANJA=(230,126,34)
VIOLETA=(155,89,182); CIAN=(26,188,156); AMARILLO=(241,196,15); NEGRO=(0,0,0)

BASE_DIR=Path(__file__).resolve().parent.parent
OS_DIR=BASE_DIR/'os'; USER_DIR=BASE_DIR/'user'
KX_DIR=USER_DIR/'.Kinetix'; LOG_DIR=KX_DIR/'logs'
STORAGE_DIR=USER_DIR/'storage'; MAIN_DIR=STORAGE_DIR/'Main'
MEDIA_DIR=MAIN_DIR/'Media'; OTHER_DIR=MEDIA_DIR/'Other'; GALLERY_DIR=MEDIA_DIR/'Gallery'
LANG_FILE=KX_DIR/'language.json'; DT_FILE=KX_DIR/'datetime.json'; PIN_FILE=KX_DIR/'pin.json'
APPS_FILE=KX_DIR/'desktop_apps.json'
ICONS_DIR=KX_DIR/'icons'
SAVES_DIR=MAIN_DIR/'Saves'  # visible in Files; preserved on factory reset

for p in (OS_DIR,USER_DIR,KX_DIR,LOG_DIR,STORAGE_DIR,MAIN_DIR,MEDIA_DIR,OTHER_DIR,GALLERY_DIR,ICONS_DIR,SAVES_DIR):
    p.mkdir(parents=True,exist_ok=True)

pygame.init()
pygame.key.set_repeat(0)

canvas=pygame.Surface((ANCHO,ALTO))
# Ventana (no pantalla completa)
pantalla=pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption('Kinetix 1.0')

# Fuentes actualizadas a Noto Sans (con respaldo en Arial o fuentes del sistema)
fuente15=pygame.font.SysFont('notosans,arial',15)
fuente19=pygame.font.SysFont('notosans,arial',19)
fuente23=pygame.font.SysFont('notosans,arial',23)
fuente29=pygame.font.SysFont('notosans,arial',29)
fuente40=pygame.font.SysFont('notosans,arial',40,bold=True)

# Variable con los formatos reconocidos divididos en imágenes, textos y paquetes de aplicación (.kap)
FORMATOS_SOPORTADOS = {
    'imagenes': {'.png', '.jpg', '.jpeg', '.webp', '.bmp'},
    'textos': {'.txt'},
    'paquetes': {'.kap'},
    'saves': {'.save'}
}

idioma='en'
app_actual='desktop'
pantalla_anterior='desktop'
running=True

ajuste_seccion=None
toast_text=''
toast_until=0

# Gallery navigation state
gallery_mode='grid' # 'grid' or 'detail'
gallery_selected_image=None

# Variables para el Modo Terminal interactivo y apps visuales con .kap
kap_terminal_active = False
kap_terminal_output = []
kap_waiting_input = False
kap_input_prompt = ""
kap_input_result = None
kap_thread = None
kap_visual_surface = None

# Installed .kap shortcuts on the desktop (list of {name, path})
desktop_apps = []

# Pending .kap when asking to update an existing app with the same name
pending_kap_path = None
pending_kap_name = None

# First-time / post-factory setup wizard (blocks Home and Back)
setup_mode = False

virtual={
    'day':1,
    'month':1,
    'year':2026,
    'hour':0,
    'minute':0
}

last_tick=pygame.time.get_ticks()
minute_acc=0

pin_hash=''
pin_enabled=False
pin_attempts=0
pin_locked_until=0

lock_mode='none'
lock_gesture_start=None
lock_gesture_y=0
lock_pin_entry=''

last_touch_ms=0

keyboard=None
selected_path=None
explorer_mode='normal'
explorer_dir=MAIN_DIR

notes_text=''
notes_path=None

calculator_text=''

game_x=200
game_y=360
game_score=0
game_target=(100,300)

error_info=None
error_scroll=0

scroll_y=0
drag_active=False
drag_start_y=0
drag_start_scroll=0
drag_moved=False
last_finger_ms=0

date_drag_field=None
date_drag_last_y=0


T={
'en':{
'home':'Home',
'settings':'Settings',
'games':'Games',
'gallery':'Gallery',
'calculator':'Calculator',
'notes':'Notes',
'files':'Files',
'power':'Power options',
'datetime':'Date & Time',
'system':'System',
'pin':'PIN',
'information':'System information',
'language':'Language',
'factory':'Factory reset',
'back':'Back',
'english':'English',
'spanish':'Español',
'day':'Day',
'month':'Month',
'year':'Year',
'hour':'Hour',
'minute':'Minute',
'save':'Save',
'cancel':'Cancel',
'accept':'Accept',
'create':'Create',
'open':'Open',
'saveas':'Save as',
'close':'Close',
'archive':'File',
'newfile':'New file',
'newfolder':'New folder',
'delete':'Delete',
'up':'Up',
'choose':'Choose',
'set':'Set',
'skip':'Skip',
'current':'Current',
'system_info':'System information',
'version':'Version',
'device':'Device',
'renderer':'Graphics renderer',
'python':'Python',
'pygame':'Pygame',
'os':'Operating system',
'machine':'Machine',
'processor':'Processor',
'driver':'Display driver',
'folder':'Folder',
'file':'File',
'no_files':'No files here',
'type_name':'Enter file name',
'enter_text':'Tap the work area to type',
'calculator_help':'Enter an expression',
'clear':'Clear',
'equal':'=',
'catch':'Catch the circle',
'score':'Score',
'power_off':'Power off',
'restart':'Restart',
'lock':'Lock',
'continue':'Continue normally',
'repair':'Repair',
'slide':'Slide to unlock',
'enter_pin':'Enter PIN',
'wrong_pin':'Incorrect PIN',
'wait':'Too many attempts. Wait',
'seconds':'seconds',
'pin_current':'Enter current PIN',
'new_pin':'Enter new 4-digit PIN',
'repeat_pin':'Repeat the PIN',
'pin_ok':'PIN configured successfully',
'pin_bad':'PINs do not match',
'pin_invalid':'PIN must contain 4 digits',
'pin_disabled':'PIN disabled successfully',
'enable_pin':'Set PIN',
'change_pin':'Change PIN',
'disable_pin':'Disable PIN',
'confirm_reset':'Delete all user data and reset Kinetix?',
'yes':'Yes',
'no':'No',
'boot':'KINETIX',
'python_error':'PYTHON ERROR',
'file_caused':'File',
'problem':'Problem',
'traceback':'Traceback / log',
'extra':'Extra information',
'gallery_empty':'Gallery is empty',
'tap_back':'Tap Back to return',
'locked':'Locked',
'unlock':'Unlock',
'resetting':'Restletting...',
'saved':'Saved successfully',
'created':'Created successfully',
'deleted':'Deleted successfully',
'cannot':'Cannot perform this action',
'select_folder':'Select a folder',
'select_file':'Select a text file',
'name':'Name',
'system_root':'Main storage',
'kap_install':'Installing .kap package...',
'kap_success':'Package installed successfully!',
'kap_error':'Invalid Python code in .kap package',
'kap_update_title':'Update app',
'kap_update_ask':'An app with this name is already installed. Update it?',
'kap_updated':'App updated',
'kap_not_updated':'Kept previous version',
'factory_options':'Choose how to reset',
'reset_no_backup':'Reset system (no backup)',
'reset_with_backup':'Reset system with backup',
'backup_created':'Backup created',
'backup_failed':'Could not create backup',
'restoring':'Restoring backup...',
'restore_ok':'Backup restored',
'restore_fail':'Could not restore backup',
'enter_pin_factory':'Enter PIN to continue'
},

'es':{
'home':'Inicio',
'settings':'Ajustes',
'games':'Juegos',
'gallery':'Galería',
'calculator':'Calculadora',
'notes':'Notas',
'files':'Archivos',
'power':'Opciones de apagado',
'datetime':'Fecha y hora',
'system':'Sistema',
'pin':'PIN',
'information':'Información del sistema',
'language':'Idioma',
'factory':'Restablecimiento de fábrica',
'back':'Atrás',
'english':'English',
'spanish':'Español',
'day':'Día',
'month':'Mes',
'year':'Año',
'hour':'Hora',
'minute':'Minuto',
'save':'Guardar',
'cancel':'Cancelar',
'accept':'Aceptar',
'create':'Crear',
'open':'Abrir',
'saveas':'Guardar como',
'close':'Cerrar',
'archive':'Archivo',
'newfile':'Nuevo archivo',
'newfolder':'Nueva carpeta',
'delete':'Eliminar',
'up':'Subir',
'choose':'Elegir',
'set':'Configurar',
'skip':'Omitir',
'current':'Actual',
'system_info':'Información del sistema',
'version':'Versión',
'device':'Dispositivo',
'renderer':'Renderizador gráfico',
'python':'Python',
'pygame':'Pygame',
'os':'Sistema operativo',
'machine':'Máquina',
'processor':'Procesador',
'driver':'Controlador de pantalla',
'folder':'Carpeta',
'file':'Archivo',
'no_files':'No hay archivos aquí',
'type_name':'Escribe el nombre del archivo',
'enter_text':'Toca el área de trabajo para escribir',
'calculator_help':'Escribe una expresión',
'clear':'Borrar',
'equal':'=',
'catch':'Atrapa el círculo',
'score':'Puntuación',
'power_off':'Apagar',
'restart':'Reiniciar',
'lock':'Bloquear',
'continue':'Seguir normalmente',
'repair':'Reparar',
'slide':'Desliza para desbloquear',
'enter_pin':'Ingresa el PIN',
'wrong_pin':'PIN incorrecto',
'wait':'Demasiados intentos. Espera',
'seconds':'segundos',
'pin_current':'Ingresa el PIN actual',
'new_pin':'Ingresa un PIN nuevo de 4 dígitos',
'repeat_pin':'Repite el PIN',
'pin_ok':'PIN configurado exitosamente',
'pin_bad':'Los PIN no coinciden',
'pin_invalid':'El PIN debe tener 4 dígitos',
'pin_disabled':'PIN desactivado exitosamente',
'enable_pin':'Configurar PIN',
'change_pin':'Cambiar PIN',
'disable_pin':'Desactivar PIN',
'confirm_reset':'¿Eliminar todos los datos del usuario y restablecer Kinetix?',
'yes':'Sí',
'no':'No',
'boot':'KINETIX',
'python_error':'ERROR DE PYTHON',
'file_caused':'Archivo',
'problem':'Problema',
'traceback':'Traza / registro',
'extra':'Información adicional',
'gallery_empty':'La galería está vacía',
'tap_back':'Toca Atrás para volver',
'locked':'Bloqueado',
'unlock':'Desbloquear',
'resetting':'Restableciendo...',
'saved':'Guardado exitosamente',
'created':'Creado exitosamente',
'deleted':'Eliminado exitosamente',
'cannot':'No se puede realizar esta acción',
'select_folder':'Selecciona una carpeta',
'select_file':'Selecciona un archivo de texto',
'name':'Name',
'system_root':'Almacenamiento Main',
'kap_install':'Instalando paquete .kap...',
'kap_success':'¡Paquete instalado con éxito!',
'kap_error':'Código Python inválido en el paquete .kap',
'kap_update_title':'Actualizar aplicación',
'kap_update_ask':'Ya hay una aplicación con este nombre. ¿Quieres actualizarla?',
'kap_updated':'Aplicación actualizada',
'kap_not_updated':'Se mantuvo la versión anterior',
'factory_options':'Elige cómo restablecer',
'reset_no_backup':'Resetear sistema (sin copia)',
'reset_with_backup':'Resetear sistema con copia de seguridad',
'backup_created':'Copia de seguridad creada',
'backup_failed':'No se pudo crear la copia',
'restoring':'Restaurando copia...',
'restore_ok':'Copia restaurada',
'restore_fail':'No se pudo restaurar la copia',
'enter_pin_factory':'Ingresa el PIN para continuar'
}
}


def tr(k):
    return T.get(idioma,T['en']).get(k,k)


def load_json(path,default):
    try:
        with open(path,'r',encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    with open(path,'w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=2)


def load_config():
    global idioma,virtual,pin_hash,pin_enabled,desktop_apps
    d=load_json(LANG_FILE,{})
    idioma=d.get('language','en') if d.get('language') in ('en','es') else 'en'
    dt=load_json(DT_FILE,None)
    if isinstance(dt,dict):
        for k in virtual:
            try:
                virtual[k]=int(dt.get(k,virtual[k]))
            except:
                pass
    p=load_json(PIN_FILE,{})
    pin_enabled=bool(p.get('enabled',False))
    pin_hash=p.get('pin','') if pin_enabled else ''
    desktop_apps = load_desktop_apps()


def load_desktop_apps():
    data = load_json(APPS_FILE, [])
    if not isinstance(data, list):
        return []
    result = []
    for item in data:
        if not isinstance(item, dict):
            continue
        name = str(item.get('name', '')).strip()
        path = item.get('path', '')
        if not name or not path:
            continue
        p = Path(path)
        if p.exists() and p.suffix.lower() == '.kap':
            entry = {'name': name, 'path': str(p.resolve())}
            icon_path = item.get('icon')
            if icon_path and Path(icon_path).exists():
                entry['icon'] = str(Path(icon_path).resolve())
            result.append(entry)
    return result


def save_desktop_apps():
    save_json(APPS_FILE, desktop_apps)


def draw_default_kap_icon(surf):
    """Icono por defecto: cuadrícula azul de fondo (hasta el borde) + K blanca."""
    w, h = surf.get_size()
    # Fondo azul sólido
    surf.fill(AZUL)
    # Cuadrícula blanca que llega hasta los bordes
    cell = max(4, min(w, h) // 8)
    for x in range(0, w + 1, cell):
        pygame.draw.line(surf, GRIS_CLARO, (x, 0), (x, h), 1)
    for y in range(0, h + 1, cell):
        pygame.draw.line(surf, GRIS_CLARO, (0, y), (w, y), 1)
    # Letra K centrada
    try:
        font_size = max(14, int(min(w, h) * 0.55))
        f = pygame.font.SysFont('notosans,arial', font_size, bold=True)
        txt = f.render('K', True, (255, 255, 255))
        tr = txt.get_rect(center=(w // 2, h // 2))
        surf.blit(txt, tr)
    except Exception:
        pass


def extract_kap_icon(kap_path, size=64):
    """
    Busca en el .kap la función KAP_ICON(surface) y la ejecuta de forma segura.
    Convención en el .kap:
        def KAP_ICON(surface):
            # dibuja el icono sobre surface (pygame.Surface)
            ...
    Solo se ejecuta esa función (no el resto del script) para evitar bucles.
    """
    try:
        code = Path(kap_path).read_text(encoding='utf-8')
        tree = ast.parse(code)

        func_node = None
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == 'KAP_ICON':
                func_node = node
                break
        if func_node is None:
            return None

        # Compilar y ejecutar solo la definición de KAP_ICON
        module = ast.Module(body=[func_node], type_ignores=[])
        ast.fix_missing_locations(module)
        ns = {
            '__name__': '__kap_icon_extract__',
            'pygame': pygame,
            'math': math,
        }
        exec(compile(module, str(kap_path), 'exec'), ns)
        icon_fn = ns.get('KAP_ICON')
        if not callable(icon_fn):
            return None

        out = pygame.Surface((size, size), pygame.SRCALPHA)
        out.fill((0, 0, 0, 0))
        icon_fn(out)
        # Validar que dibujó algo (no quedó totalmente transparente)
        # Si falla o está vacío, se considera inválido
        return out
    except Exception:
        return None


def find_desktop_app_by_name(name):
    for app in desktop_apps:
        if app.get('name') == name:
            return app
    return None


def find_desktop_app_by_path(path_str):
    path_str = str(Path(path_str).resolve()) if path_str else ''
    for app in desktop_apps:
        if app.get('path') == path_str:
            return app
    return None


def _build_kap_entry(kap_path):
    """Build desktop entry dict (name, path, icon) for a .kap file."""
    kap_path = Path(kap_path).resolve()
    name = kap_path.stem
    path_str = str(kap_path)
    entry = {'name': name, 'path': path_str}
    icon_file = ICONS_DIR / f'{name}.png'
    custom = extract_kap_icon(kap_path, size=64)
    try:
        if custom is not None:
            pygame.image.save(custom, str(icon_file))
        else:
            default_surf = pygame.Surface((64, 64))
            draw_default_kap_icon(default_surf)
            pygame.image.save(default_surf, str(icon_file))
        entry['icon'] = str(icon_file.resolve())
    except Exception:
        pass
    return entry


def register_kap_app(kap_path, force_update=False):
    """
    Crea o actualiza el acceso directo en el escritorio.
    - Si ya hay un .kap con el mismo nombre y force_update=False → 'needs_update'
    - force_update=True: sobrescribe el .kap instalado en el dispositivo con el nuevo
      y actualiza icono / acceso directo.
    Devuelve: 'new' | 'same' | 'updated' | 'needs_update' | 'error'
    """
    global desktop_apps
    try:
        ensure_structure()
        kap_path = Path(kap_path).resolve()
        if not kap_path.exists() or kap_path.suffix.lower() != '.kap':
            return 'error'
        name = kap_path.stem
        path_str = str(kap_path)

        existing_path = find_desktop_app_by_path(path_str)
        if existing_path and not force_update:
            return 'same'

        existing_name = find_desktop_app_by_name(name)
        if existing_name and not force_update:
            if existing_name.get('path') == path_str:
                return 'same'
            return 'needs_update'

        if force_update and existing_name:
            # Ruta del .kap ya instalado (acceso directo del escritorio)
            installed = Path(existing_name.get('path', ''))
            try:
                if installed.exists() and installed.resolve() != kap_path:
                    # Sobrescribir el archivo instalado con el contenido del nuevo .kap
                    data = kap_path.read_bytes()
                    installed.parent.mkdir(parents=True, exist_ok=True)
                    installed.write_bytes(data)
                elif not installed.exists():
                    # Si el archivo original ya no está, copiar el nuevo a su ruta
                    installed.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(kap_path), str(installed))
            except Exception:
                # Si no se puede escribir en la ruta antigua, usar la nueva
                installed = kap_path

            # Actualizar entrada del escritorio (misma ruta instalada + icono nuevo)
            entry = _build_kap_entry(installed if installed.exists() else kap_path)
            # Mantener el nombre original del acceso directo
            entry['name'] = name
            for i, app in enumerate(desktop_apps):
                if app.get('name') == name:
                    desktop_apps[i] = entry
                    break
            save_desktop_apps()
            return 'updated'

        if not existing_name and not existing_path:
            entry = _build_kap_entry(kap_path)
            desktop_apps.append(entry)
            save_desktop_apps()
            toast(name, 1500)
            return 'new'

        return 'same'
    except Exception:
        return 'error'


def ensure_structure():
    for p in (
        USER_DIR,
        KX_DIR,
        LOG_DIR,
        STORAGE_DIR,
        MAIN_DIR,
        MEDIA_DIR,
        OTHER_DIR,
        GALLERY_DIR,
        ICONS_DIR,
        SAVES_DIR
    ):
        p.mkdir(parents=True, exist_ok=True)


def safe_main_path(p):
    try:
        p=Path(p).resolve()
        root=MAIN_DIR.resolve()
        return p==root or str(p).startswith(str(root)+os.sep)
    except:
        return False


def toast(msg,ms=1800):
    global toast_text,toast_until
    toast_text=msg
    toast_until=pygame.time.get_ticks()+ms


def draw_text(
    txt,
    x,
    y,
    font=fuente19,
    color=GRIS_CLARO,
    center=False,
    surf=canvas
):
    s=font.render(str(txt),True,color)
    r=s.get_rect()
    if center:
        r.center=(x,y)
    else:
        r.topleft=(x,y)
    surf.blit(s,r)
    return r


def button(
    rect,
    label,
    color=GRIS_OSCURO,
    text_color=GRIS_CLARO,
    font=fuente15
):
    pygame.draw.rect(
        canvas,
        color,
        rect,
        border_radius=10
    )
    pygame.draw.rect(
        canvas,
        (85,89,100),
        rect,
        1,
        border_radius=10
    )
    draw_text(
        label,
        rect.centerx,
        rect.centery,
        font,
        text_color,
        True
    )


def icon(kind,cx,cy,size=46):
    if kind=='settings':
        pygame.draw.circle(canvas,GRIS_CLARO,(cx,cy),size//3)
        pygame.draw.circle(canvas,FONDO_APP,(cx,cy),size//6)
        for i in range(8):
            a=i*math.pi/4
            x=cx+int(math.cos(a)*size*.38)
            y=cy+int(math.sin(a)*size*.38)
            pygame.draw.rect(canvas,GRIS_CLARO,(x-4,y-7,8,14),border_radius=2)
    elif kind=='games':
        r=pygame.Rect(cx-size//2,cy-size//4,size,size//2)
        pygame.draw.rect(canvas,AZUL,r,border_radius=12)
        pygame.draw.line(canvas,GRIS_CLARO,(cx-size//4,cy),(cx-size//4+16,cy),4)
        pygame.draw.line(canvas,GRIS_CLARO,(cx-size//4+8,cy-8),(cx-size//4+8,cy+8),4)
        pygame.draw.circle(canvas,ROJO,(cx+size//4,cy-5),4)
        pygame.draw.circle(canvas,AMARILLO,(cx+size//3,cy+6),4)
    elif kind=='gallery':
        r=pygame.Rect(cx-size//2,cy-size//2,size,size)
        pygame.draw.rect(canvas,GRIS_CLARO,r,border_radius=5)
        pygame.draw.circle(canvas,AMARILLO,(cx+10,cy-12),5)
        pygame.draw.polygon(canvas,GRIS_OSCURO,[
            (cx-size//2+5,cy+size//4),
            (cx-3,cy-2),
            (cx+10,cy+10),
            (cx+size//2-5,cy-size//8),
            (cx+size//2-5,cy+size//2-5),
            (cx-size//2+5,cy+size//2-5)
        ])
    elif kind=='calculator':
        r=pygame.Rect(cx-size//2,cy-size//2,size,size)
        pygame.draw.rect(canvas,VIOLETA,r,border_radius=6)
        pygame.draw.rect(canvas,FONDO_APP,(cx-size//3,cy-size//3,size*2//3,13),border_radius=2)
        for yy in range(3):
            for xx in range(3):
                pygame.draw.circle(canvas,GRIS_CLARO,(cx-size//4+xx*12,cy+4+yy*12),3)
    elif kind=='notes':
        r=pygame.Rect(cx-size//2,cy-size//2,size,size)
        pygame.draw.rect(canvas,AMARILLO,r,border_radius=4)
        pygame.draw.polygon(canvas,FONDO_APP,[
            (cx+size//4,cy-size//2),
            (cx+size//2,cy-size//4),
            (cx+size//4,cy-size//4)
        ])
        pygame.draw.line(canvas,GRIS_OSCURO,(cx-size//3,cy),(cx+size//3,cy),2)
        pygame.draw.line(canvas,GRIS_OSCURO,(cx-size//3,cy+10),(cx+size//3,cy+10),2)
    elif kind=='files':
        pts=[
            (cx-size//2,cy-size//3),
            (cx-size//5,cy-size//3),
            (cx-size//10,cy-size//2),
            (cx+size//2,cy-size//2),
            (cx+size//2,cy+size//3),
            (cx-size//2,cy+size//3)
        ]
        pygame.draw.polygon(canvas,AMARILLO,pts)
        pygame.draw.line(canvas,(210,160,20),(cx-size//5,cy-size//3),(cx+size//2-2,cy-size//3),3)
    elif kind=='download':
        r=pygame.Rect(cx-size//2,cy-size//2,size,size)
        pygame.draw.rect(canvas,CIAN,r,border_radius=8)
        pygame.draw.line(canvas,NEGRO,(cx,cy-size//4),(cx,cy+size//6),4)
        pygame.draw.polygon(canvas,NEGRO,[(cx-size//4,cy), (cx,cy+size//4), (cx+size//4,cy)])
        pygame.draw.line(canvas,NEGRO,(cx-size//3,cy+size//3),(cx+size//3,cy+size//3),3)
    elif kind=='power':
        pygame.draw.arc(canvas,ROJO,(cx-size//2,cy-size//2,size,size),math.radians(45),math.radians(315),6)
        pygame.draw.line(canvas,ROJO,(cx,cy-size//2+3),(cx,cy+5),6)
    elif kind == 'app':
        # Default: blue grid to the edges + white K (no badge)
        r = pygame.Rect(cx - size // 2, cy - size // 2, size, size)
        tmp = pygame.Surface((size, size))
        draw_default_kap_icon(tmp)
        canvas.blit(tmp, r.topleft)
        pygame.draw.rect(canvas, (40, 90, 140), r, 1, border_radius=4)
    elif kind == 'cloud' or kind == 'save':
        # Nubecita (icono de copia de seguridad .save)
        r = pygame.Rect(cx - size // 2, cy - size // 2, size, size)
        pygame.draw.rect(canvas, (70, 130, 180), r, border_radius=10)
        # cloud body
        pygame.draw.circle(canvas, GRIS_CLARO, (cx - 8, cy + 2), size // 5)
        pygame.draw.circle(canvas, GRIS_CLARO, (cx + 6, cy), size // 4)
        pygame.draw.circle(canvas, GRIS_CLARO, (cx + 14, cy + 4), size // 6)
        pygame.draw.ellipse(canvas, GRIS_CLARO, (cx - size // 3, cy + 2, size * 2 // 3, size // 4))


def home_bar():
    pygame.draw.rect(canvas,BARRA,(0,ALTO-62,ANCHO,62))
    pygame.draw.circle(canvas,GRIS_CLARO,(ANCHO//2,ALTO-31),22)
    pygame.draw.circle(canvas,BARRA,(ANCHO//2,ALTO-31),17)


def status():
    pygame.draw.rect(canvas,BARRA,(0,0,ANCHO,32))
    draw_text('Kinetix',10,7,fuente15,GRIS_CLARO)
    draw_text(f'{virtual["hour"]:02d}:{virtual["minute"]:02d}',ANCHO-58,7,fuente15,GRIS_CLARO)


def presentar():
    global pantalla
    try:
        w, h = pantalla.get_size()
        if w <= 0 or h <= 0:
            return
        escala = min(w / ANCHO, h / ALTO)
        if escala <= 0:
            return
        sw = int(ANCHO * escala)
        sh = int(ALTO * escala)
        if sw <= 0 or sh <= 0:
            return
        ox = (w - sw) // 2
        oy = (h - sh) // 2
        pantalla.fill((0, 0, 0))
        scaled = pygame.transform.smoothscale(canvas, (sw, sh))
        pantalla.blit(scaled, (ox, oy))
        pygame.display.flip()
    except pygame.error as e:
        msg = str(e).lower()
        if 'egl' in msg or 'context' in msg or 'display' in msg:
            try:
                pantalla = pygame.display.set_mode((ANCHO, ALTO))
            except Exception:
                pass
        else:
            raise
    except Exception:
        try:
            pantalla = pygame.display.set_mode((ANCHO, ALTO))
        except Exception:
            pass


def posicion_logica(pos):
    try:
        w, h = pantalla.get_size()
        if w <= 0 or h <= 0:
            return pos
        escala = min(w / ANCHO, h / ALTO)
        if escala <= 0:
            return pos
        sw = int(ANCHO * escala)
        sh = int(ALTO * escala)
        ox = (w - sw) // 2
        oy = (h - sh) // 2
        return ((pos[0] - ox) / escala, (pos[1] - oy) / escala)
    except Exception:
        return pos


def hit(r,x,y):
    return r.collidepoint(x,y)


def month_name(i):
    en=[
        'January','February','March','April',
        'May','June','July','August',
        'September','October','November','December'
    ]
    es=[
        'Enero','Febrero','Marzo','Abril',
        'Mayo','Junio','Julio','Agosto',
        'Septiembre','Octubre','Noviembre','Diciembre'
    ]
    return (es if idioma=='es' else en)[max(1,min(12,i))-1]


def save_datetime():
    save_json(DT_FILE,virtual)


def tick_clock():
    global last_tick,minute_acc,virtual
    now=pygame.time.get_ticks()
    d=max(0,now-last_tick)
    last_tick=now
    minute_acc+=d
    while minute_acc>=60000:
        minute_acc-=60000
        virtual['minute']+=1
        if virtual['minute']>=60:
            virtual['minute']=0
            virtual['hour']+=1
        if virtual['hour']>=24:
            virtual['hour']=0
            virtual['day']+=1
        if virtual['day']>31:
            virtual['day']=1
            virtual['month']+=1
        if virtual['month']>12:
            virtual['month']=1
            virtual['year']+=1
    if d:
        save_datetime()


def top(title,back=True):
    status()
    draw_text(title,ANCHO//2,55,fuente23,GRIS_CLARO,True)
    if back:
        button(pygame.Rect(12,40,72,32),tr('back'))


def get_desktop_app_positions():
    """Positions for built-in apps + installed .kap shortcuts (4 columns).
    Each entry: (kind, label, x, y, kap_path_or_None, icon_path_or_None)
    """
    base = [
        ('settings', tr('settings'), 20, 90, None, None),
        ('games', tr('games'), 110, 90, None, None),
        ('gallery', tr('gallery'), 200, 90, None, None),
        ('calculator', tr('calculator'), 290, 90, None, None),
        ('notes', tr('notes'), 20, 220, None, None),
        ('files', tr('files'), 110, 220, None, None),
        ('power', tr('power'), 200, 220, None, None),
    ]
    cols = 4
    start_idx = 7
    for i, app in enumerate(desktop_apps):
        idx = start_idx + i
        col = idx % cols
        row = idx // cols
        x = 20 + col * 90
        y = 90 + row * 130
        if y + 80 > ALTO - 70:
            break
        name = app.get('name', 'App')[:10]
        base.append(('app', name, x, y, app.get('path'), app.get('icon')))
    return base


def draw_desktop():
    canvas.fill(FONDO)
    status()
    draw_text('Kinetix 1.0', ANCHO // 2, 55, fuente29, GRIS_CLARO, True)
    for k, n, x, y, _path, icon_path in get_desktop_app_positions():
        pygame.draw.rect(canvas, FONDO_APP, (x, y, 80, 80), border_radius=14)
        if k == 'app' and icon_path and Path(icon_path).exists():
            try:
                im = pygame.image.load(str(icon_path)).convert_alpha()
                im = pygame.transform.smoothscale(im, (52, 52))
                canvas.blit(im, (x + 14, y + 6))
            except Exception:
                icon('app', x + 40, y + 32, 44)
        else:
            icon(k, x + 40, y + 32, 44)
        draw_text(n, x + 40, y + 66, fuente15, GRIS_CLARO, True)
    home_bar()


def draw_settings():
    canvas.fill(FONDO_APP)
    top(tr('settings'),False)
    button(pygame.Rect(25,85,350,62),tr('datetime'),AZUL)
    button(pygame.Rect(25,160,350,62),tr('system'),VIOLETA)
    button(pygame.Rect(25,235,350,62),tr('pin'),CIAN)
    draw_text(tr('system_info'),ANCHO//2,335,fuente15,GRIS,True)
    home_bar()


def draw_datetime():
    canvas.fill(FONDO_APP)
    # En setup: sin Atrás; en Ajustes: con Atrás
    top(tr('datetime'), back=not setup_mode)
    fields = [
        ('day', f'{tr("day")}: {virtual["day"]}'),
        ('month', f'{tr("month")}: {month_name(virtual["month"])}'),
        ('year', f'{tr("year")}: {virtual["year"]}'),
        ('hour', f'{tr("hour")}: {virtual["hour"]}'),
        ('minute', f'{tr("minute")}: {virtual["minute"]}')
    ]
    for i, (k, v) in enumerate(fields):
        r = pygame.Rect(25, 90 + i * 58, 350, 45)
        button(r, v, GRIS_OSCURO)
        draw_text('Swipe', 350, r.centery, fuente15, GRIS, True)
    draw_text(
        tr('current') + f': {virtual["day"]}/{virtual["month"]}/{virtual["year"]}  {virtual["hour"]:02d}:{virtual["minute"]:02d}',
        200, 390, fuente15, GRIS_CLARO, True
    )
    draw_text(
        'Desliza dentro de un campo para cambiar su valor.' if idioma == 'es' else 'Swipe inside a field to change its value.',
        200, 420, fuente15, GRIS, True
    )
    if setup_mode:
        # Botón para terminar la configuración inicial
        button(pygame.Rect(40, 460, 320, 50), tr('continue'), VERDE, font=fuente19)
    else:
        home_bar()


def adjust_field(field,delta):
    if field=='day':
        virtual['day']=max(1,min(31,virtual['day']+delta))
    elif field=='month':
        virtual['month']=max(1,min(12,virtual['month']+delta))
    elif field=='year':
        virtual['year']=max(2026,min(2126,virtual['year']+delta))
    elif field=='hour':
        virtual['hour']=(virtual['hour']+delta)%24
    elif field=='minute':
        virtual['minute']=(virtual['minute']+delta)%60
    save_datetime()


def draw_system():
    canvas.fill(FONDO_APP)
    top(tr('system'),True)
    button(pygame.Rect(25,90,350,55),tr('information'),AZUL)
    button(pygame.Rect(25,155,350,55),tr('language'),VIOLETA)
    button(pygame.Rect(25,220,350,55),tr('factory'),ROJO)
    home_bar()


def get_real_processor():
    try:
        name = platform.processor().strip()
        if name:
            return name
    except Exception:
        pass
    try:
        name = platform.uname().processor.strip()
        if name:
            return name
    except Exception:
        pass
    return 'No disponible'


def draw_system_info():
    canvas.fill(FONDO_APP)
    top(tr('information'),True)
    lines=[
        f'{tr("version")}: Kinetix 1.0',
        f'{tr("device")}: Kinetix',
        f'{tr("renderer")}: Pygame',
        f'{tr("python")}: {platform.python_version()}',
        f'{tr("pygame")}: {pygame.version.ver}',
        f'{tr("os")}: Kinetix',
        f'{tr("machine")}: Kinetix',
        f'{tr("processor")}: {get_real_processor()}',
        f'{tr("driver")}: Pygame',
        'SDL: '+'.'.join(map(str,pygame.get_sdl_version()))
    ]
    y=90-scroll_y
    for line in lines:
        draw_text(line,20,y,fuente15,GRIS_CLARO)
        y+=34
    home_bar()


def draw_language():
    canvas.fill(FONDO_APP)
    # En setup inicial: sin botón Atrás
    top(tr('language'), back=not setup_mode)
    if setup_mode:
        draw_text(
            'Choose your language' if idioma == 'en' else 'Elige tu idioma',
            200, 75, fuente15, GRIS, True
        )
    button(pygame.Rect(30, 100, 340, 65), tr('english'), AZUL)
    button(pygame.Rect(30, 180, 340, 65), tr('spanish'), VERDE)
    if not setup_mode:
        home_bar()


def load_pin():
    global pin_enabled,pin_hash
    d=load_json(PIN_FILE,{})
    pin_enabled=bool(d.get('enabled',False))
    pin_hash=d.get('pin','') if pin_enabled else ''


def set_pin(p):
    global pin_enabled,pin_hash
    pin_enabled=True
    pin_hash=p
    save_json(PIN_FILE,{'enabled':True,'pin':p})


def disable_pin():
    global pin_enabled,pin_hash
    pin_enabled=False
    pin_hash=''
    save_json(PIN_FILE,{'enabled':False,'pin':''})
    toast(tr('pin_disabled'))


def draw_pin():
    canvas.fill(FONDO_APP)
    top(tr('pin'),True)
    if pin_enabled:
        draw_text(tr('change_pin'),200,105,fuente19,GRIS_CLARO,True)
        button(pygame.Rect(30,145,340,55),tr('change_pin'),AZUL)
        button(pygame.Rect(30,215,340,55),tr('disable_pin'),ROJO)
    else:
        draw_text(tr('enable_pin'),200,105,fuente19,GRIS_CLARO,True)
        button(pygame.Rect(30,145,340,55),tr('enable_pin'),CIAN)
    home_bar()


def create_system_backup():
    """Crea un archivo .save en Saves/ con el estado actual del usuario.
    No incluye otros .save dentro del zip (evita corrupción al restaurar).
    """
    try:
        ensure_structure()
        SAVES_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        save_path = SAVES_DIR / f'Kinetix_{ts}.save'
        saves_resolved = SAVES_DIR.resolve()

        with zipfile.ZipFile(str(save_path), 'w', zipfile.ZIP_DEFLATED) as zf:
            # Meta primero (marca el archivo como backup válido)
            meta = {
                'version': '1.0',
                'created': ts,
                'type': 'kinetix_backup'
            }
            zf.writestr('meta.json', json.dumps(meta, ensure_ascii=False, indent=2))

            # Config Kinetix
            for conf in (LANG_FILE, DT_FILE, PIN_FILE, APPS_FILE):
                if conf.exists() and conf.is_file():
                    zf.write(str(conf), arcname=f'config/{conf.name}')

            # Iconos de apps
            if ICONS_DIR.exists():
                for ic in ICONS_DIR.iterdir():
                    if ic.is_file():
                        zf.write(str(ic), arcname=f'icons/{ic.name}')

            # Almacenamiento Main (sin la carpeta Saves ni archivos .save)
            if MAIN_DIR.exists():
                for root, dirs, files in os.walk(MAIN_DIR):
                    root_path = Path(root).resolve()
                    # No entrar en Saves
                    try:
                        if root_path == saves_resolved or saves_resolved in root_path.parents:
                            dirs[:] = []
                            continue
                    except Exception:
                        pass
                    # Filtrar subdirs llamados Saves
                    dirs[:] = [d for d in dirs if d.lower() != 'saves']
                    for fn in files:
                        if fn.lower().endswith('.save'):
                            continue
                        fp = Path(root) / fn
                        try:
                            rel = fp.relative_to(USER_DIR)
                            zf.write(str(fp), arcname=str(rel).replace('\\', '/'))
                        except Exception:
                            pass

        # Verificar que el zip se puede abrir
        with zipfile.ZipFile(str(save_path), 'r') as chk:
            if 'meta.json' not in chk.namelist():
                save_path.unlink(missing_ok=True)
                return None
        return save_path
    except Exception:
        return None


def restore_from_save(save_path):
    """Restaura el sistema desde un archivo .save y reinicia.
    Acepta zips Kinetix (con o sin meta estricto). No modifica la carpeta Saves.
    """
    global desktop_apps, idioma, virtual, pin_hash, pin_enabled
    tmp_dir = None
    try:
        save_path = Path(str(save_path)).resolve()
        if not save_path.exists():
            toast(tr('restore_fail') + ' (no file)')
            return False
        if save_path.suffix.lower() != '.save':
            toast(tr('restore_fail') + ' (ext)')
            return False

        # Abrir como zip (los .save son ZIP)
        try:
            zf = zipfile.ZipFile(str(save_path), 'r')
        except zipfile.BadZipFile:
            toast(tr('restore_fail') + ' (zip)')
            return False
        except Exception as e:
            toast(tr('restore_fail') + f' ({type(e).__name__})')
            return False

        toast(tr('restoring'), 2000)
        presentar()

        tmp_dir = BASE_DIR / ('_restore_tmp_' + str(int(time.time())))
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir, ignore_errors=True)
        tmp_dir.mkdir(parents=True, exist_ok=True)

        try:
            zf.extractall(str(tmp_dir))
        finally:
            zf.close()

        restored_something = False

        # Configs
        cfg_map = {
            'language.json': LANG_FILE,
            'datetime.json': DT_FILE,
            'pin.json': PIN_FILE,
            'desktop_apps.json': APPS_FILE,
        }
        cfg_src = tmp_dir / 'config'
        if cfg_src.exists():
            for name, dest in cfg_map.items():
                src = cfg_src / name
                if src.is_file():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(src), str(dest))
                    restored_something = True

        # Iconos
        icons_src = tmp_dir / 'icons'
        if icons_src.exists():
            ICONS_DIR.mkdir(parents=True, exist_ok=True)
            for ic in icons_src.iterdir():
                if ic.is_file():
                    shutil.copy2(str(ic), str(ICONS_DIR / ic.name))
                    restored_something = True

        # Storage
        storage_src = tmp_dir / 'storage'
        if storage_src.exists():
            for root, dirs, files in os.walk(storage_src):
                dirs[:] = [d for d in dirs if d.lower() != 'saves']
                for fn in files:
                    if fn.lower().endswith('.save'):
                        continue
                    src_fp = Path(root) / fn
                    try:
                        rel = src_fp.relative_to(tmp_dir)
                    except Exception:
                        continue
                    dest_fp = USER_DIR / rel
                    try:
                        dest_res = dest_fp.resolve()
                        saves_res = SAVES_DIR.resolve()
                        if dest_res == saves_res or saves_res in dest_res.parents:
                            continue
                    except Exception:
                        pass
                    dest_fp.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(src_fp), str(dest_fp))
                    restored_something = True

        shutil.rmtree(str(tmp_dir), ignore_errors=True)
        tmp_dir = None

        if not restored_something:
            toast(tr('restore_fail') + ' (empty)')
            return False

        load_config()
        desktop_apps = load_desktop_apps()
        toast(tr('restore_ok'), 1500)
        restart_process(delay=700)
        return True
    except Exception as e:
        if tmp_dir is not None:
            try:
                shutil.rmtree(str(tmp_dir), ignore_errors=True)
            except Exception:
                pass
        toast(tr('restore_fail') + f' ({type(e).__name__})')
        return False


def reset_user(with_backup=False):
    """Restablece de fábrica. La carpeta Saves siempre se preserva (con o sin copia nueva)."""
    global desktop_apps, idioma, virtual, pin_hash, pin_enabled, pin_attempts, pin_locked_until
    try:
        if with_backup:
            path = create_system_backup()
            if path is None:
                toast(tr('backup_failed'), 2000)
                return
            toast(tr('backup_created') + f': {path.name}', 1800)
            presentar()
            pygame.time.delay(800)

        ensure_structure()

        # Mover Saves fuera de USER_DIR para que rmtree no la toque nunca
        park = BASE_DIR / '_kinetix_saves_park'
        if park.exists():
            shutil.rmtree(park, ignore_errors=True)

        if SAVES_DIR.exists():
            park.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(SAVES_DIR), str(park))
            except Exception:
                # Fallback: copiar archivos
                park.mkdir(parents=True, exist_ok=True)
                for f in SAVES_DIR.iterdir():
                    if f.is_file() and f.suffix.lower() == '.save':
                        try:
                            shutil.copy2(str(f), str(park / f.name))
                        except Exception:
                            pass

        # Recoger .save sueltos fuera de Saves
        extra_park = []
        if USER_DIR.exists():
            for root, dirs, files in os.walk(USER_DIR):
                for fn in files:
                    if fn.lower().endswith('.save'):
                        fp = Path(root) / fn
                        try:
                            extra_park.append((fn, fp.read_bytes()))
                        except Exception:
                            pass

        if USER_DIR.exists():
            shutil.rmtree(USER_DIR, ignore_errors=True)

        ensure_structure()
        SAVES_DIR.mkdir(parents=True, exist_ok=True)

        # Devolver Saves
        if park.exists():
            for f in park.iterdir():
                if f.is_file():
                    try:
                        shutil.copy2(str(f), str(SAVES_DIR / f.name))
                    except Exception:
                        pass
            shutil.rmtree(park, ignore_errors=True)

        for name, data in extra_park:
            dest = SAVES_DIR / name
            if not dest.exists():
                try:
                    dest.write_bytes(data)
                except Exception:
                    pass

        # Estado en memoria limpio
        desktop_apps = []
        idioma = 'en'
        virtual = {'day': 1, 'month': 1, 'year': 2026, 'hour': 0, 'minute': 0}
        pin_hash = ''
        pin_enabled = False
        pin_attempts = 0
        pin_locked_until = 0

        toast(tr('resetting'), 900)
        restart_process(delay=450)
    except Exception as e:
        prepare_error(e)


def restart_process(delay=350):
    canvas.fill(NEGRO)
    draw_text(tr('boot'),200,300,fuente40,GRIS_CLARO,True)
    presentar()
    pygame.time.delay(delay)
    boot()


def power_off():
    canvas.fill(NEGRO)
    presentar()
    pygame.time.delay(400)
    pygame.quit()
    raise SystemExit


def draw_power():
    canvas.fill(FONDO_APP)
    top(tr('power'),True)
    items=[
        ('lock', CIAN),
        ('restart', AZUL),
        ('power_off', ROJO)
    ]
    for i,(k,c) in enumerate(items):
        button(
            pygame.Rect(35,110+i*75,330,60),
            tr(k),
            c,
            text_color=GRIS_CLARO,
            font=fuente19
        )
    home_bar()


def draw_lock():
    canvas.fill(NEGRO)
    if lock_mode=='slide':
        draw_text('Kinetix',200,170,fuente40,GRIS_CLARO,True)
        draw_text(tr('slide'),200,420,fuente23,GRIS_CLARO,True)
        pygame.draw.line(canvas,GRIS_OSCURO,(80,470),(320,470),6)
        pygame.draw.circle(canvas,GRIS_CLARO,(200,470),20)
        draw_text(f'{virtual["hour"]:02d}:{virtual["minute"]:02d}',200,225,fuente29,GRIS,True)
    else:
        draw_text('Kinetix',200,100,fuente40,GRIS_CLARO,True)
        draw_text(tr('enter_pin'),200,150,fuente19,GRIS,True)
        if pin_locked_until>pygame.time.get_ticks():
            sec=max(0,math.ceil((pin_locked_until-pygame.time.get_ticks())/1000))
            draw_text(f'{tr("wait")} {sec} {tr("seconds")}',200,210,fuente19,ROJO,True)
        else:
            draw_text(('• ' * len(lock_pin_entry)).strip() or '○ ○ ○ ○',200,215,fuente29,GRIS_CLARO,True)
            for i,n in enumerate(['1','2','3','4','5','6','7','8','9','0']):
                row=i//3
                col=i%3
                if i==9:
                    r=pygame.Rect(150,500,100,48)
                else:
                    r=pygame.Rect(70+col*90,275+row*65,70,50)
                button(r,n,GRIS_OSCURO)


def open_keyboard(
    mode='text',
    value='',
    title='',
    callback=None
):
    global keyboard
    keyboard={
        'mode':mode,
        'value':value,
        'title':title,
        'callback':callback,
        'shift':False
    }


def keyboard_draw():
    global keyboard
    if not keyboard:
        return
    pygame.draw.rect(canvas,(18,20,27),(0,300,400,238))
    draw_text(keyboard['title'],200,318,fuente19,GRIS_CLARO,True)
    draw_text(keyboard['value'][-35:],200,345,fuente19,AZUL,True)
    if keyboard['mode']=='numeric':
        keys=list('1234567890')
        positions=[]
        for i,k in enumerate(keys):
            positions.append((k,50+(i%3)*105,370+(i//3)*45,90,38))
        positions+=[('⌫',260,505,60,32),('OK',315,505,70,32)]
    else:
        rows=[
            list('1234567890'),
            list('qwertyuiop'),
            list('asdfghjklñ'),
            ['SHIFT','z','x','c','v','b','n','m','⌫'],
            ['SPACE','ENTER','OK']
        ]
        positions=[]
        for ri,row in enumerate(rows):
            y=370+ri*34
            if ri<3:
                ww=35
                start=(400-len(row)*ww)//2
                for j,k in enumerate(row):
                    positions.append((k,start+j*ww,y,32,29))
            elif ri==3:
                ww=39
                start=5
                for j,k in enumerate(row):
                    positions.append((k,start+j*ww,y,37 if k not in ('SHIFT','⌫') else 55,29))
            else:
                positions+=[
                    ('SPACE',8,y,210,29),
                    ('ENTER',223,y,80,29),
                    ('OK',310,y,82,29)
                ]
    for k,x,y,w,h in positions:
        button(
            pygame.Rect(x,y,w,h),
            tr('accept') if k=='OK' else k,
            AZUL if k in ('OK','ENTER') else GRIS_OSCURO,
            GRIS_CLARO,
            fuente15
        )


def keyboard_key(x,y):
    global keyboard
    if not keyboard:
        return
    mode=keyboard['mode']
    if mode=='numeric':
        keys=list('1234567890')
        for i,k in enumerate(keys):
            r=pygame.Rect(50+(i%3)*105,370+(i//3)*45,90,38)
            if r.collidepoint(x,y):
                keyboard['value']+=k
                return
        if pygame.Rect(260,505,60,32).collidepoint(x,y):
            keyboard['value']=keyboard['value'][:-1]
            return
        if pygame.Rect(315,505,70,32).collidepoint(x,y):
            finish_keyboard()
            return
    else:
        rows=[
            list('1234567890'),
            list('qwertyuiop'),
            list('asdfghjklñ'),
            ['SHIFT','z','x','c','v','b','n','m','⌫']
        ]
        for ri,row in enumerate(rows):
            y0=370+ri*34
            if ri<3:
                ww=35
                start=(400-len(row)*ww)//2
                for j,k in enumerate(row):
                    r=pygame.Rect(start+j*ww,y0,32,29)
                    if r.collidepoint(x,y):
                        if k.isalpha():
                            keyboard['value']+=(k.upper() if keyboard.get('shift') else k)
                            keyboard['shift']=False
                        else:
                            keyboard['value']+=k
                        return
            else:
                ww=39
                start=5
                for j,k in enumerate(row):
                    w=37 if k not in ('SHIFT','⌫') else 55
                    r=pygame.Rect(start+j*ww,y0,w,29)
                    if r.collidepoint(x,y):
                        if k=='SHIFT':
                            keyboard['shift']=not keyboard.get('shift',False)
                        elif k=='⌫':
                            keyboard['value']=keyboard['value'][:-1]
                        else:
                            keyboard['value']+=k
                        return
        y0=370+4*34
        if pygame.Rect(8,y0,210,29).collidepoint(x,y):
            keyboard['value']+=' '
            return
        if pygame.Rect(223,y0,80,29).collidepoint(x,y):
            keyboard['value']+='\n'
            return
        if pygame.Rect(310,y0,82,29).collidepoint(x,y):
            finish_keyboard()


def finish_keyboard():
    global keyboard
    if not keyboard:
        return
    cb=keyboard.get('callback')
    value=keyboard.get('value','')
    keyboard=None
    if cb:
        cb(value)


def draw_notes():
    canvas.fill(FONDO_APP)
    top(tr('notes'),False)
    button(pygame.Rect(8,40,90,34),tr('open'),AZUL)
    button(pygame.Rect(108,40,90,34),tr('save'),VERDE)
    pygame.draw.rect(canvas,(25,27,35),(18,115,364,330),border_radius=8)
    draw_text(notes_text or tr('enter_text'),25,125,fuente15,GRIS_CLARO)
    home_bar()


def draw_explorer(save_mode=False):
    canvas.fill(FONDO_APP)
    top(tr('files'),True)
    draw_text(str(explorer_dir.name),200,88,fuente19,GRIS_CLARO,True)
    entries=list_entries()
    y=112-scroll_y
    for p in entries:
        if selected_path == p:
            pygame.draw.rect(canvas, AZUL, (15, y, 370, 38), border_radius=6)

        if p.is_dir():
            icon_kind = 'files'
        elif p.suffix.lower() in FORMATOS_SOPORTADOS['imagenes']:
            icon_kind = 'gallery'
        elif p.suffix.lower() in FORMATOS_SOPORTADOS['textos']:
            icon_kind = 'notes'
        elif p.suffix.lower() in FORMATOS_SOPORTADOS['paquetes']:
            icon_kind = 'download'
        elif p.suffix.lower() in FORMATOS_SOPORTADOS['saves']:
            icon_kind = 'cloud'
        else:
            icon_kind = 'files'

        icon(icon_kind,35,y+15,30)
        draw_text(p.name,60,y+5,fuente15,GRIS_CLARO)
        y+=44
    if not entries:
        draw_text(tr('no_files'),200,260,fuente19,GRIS,True)
    if explorer_mode=='notes_save':
        button(pygame.Rect(15,455,240,40),tr('type_name'),AZUL)
        button(pygame.Rect(265,455,120,40),tr('save'),VERDE)
    elif explorer_mode=='notes_open':
        button(pygame.Rect(280,455,100,40),tr('open'),AZUL)
    home_bar()


def list_entries():
    try:
        return [
            p for p in sorted(explorer_dir.iterdir(),key=lambda p:(not p.is_dir(),p.name.lower()))
            if not p.name.startswith('.')
        ]
    except:
        return []


def select_explorer_at(x,y):
    global selected_path,explorer_dir
    idx=int((y-112+scroll_y)//44)
    arr=list_entries()
    if 0<=idx<len(arr):
        p=arr[idx]
        if p.is_dir():
            explorer_dir=p
            reset_scroll()
        else:
            if p.suffix.lower() in FORMATOS_SOPORTADOS['imagenes']:
                toast(tr('cannot'))
                return
            selected_path=p


def inspect_and_run_kap_package(kap_path, skip_update_check=False):
    """Inspecciona si el paquete .kap importa librerías visuales o de consola."""
    global app_actual, kap_terminal_active, kap_terminal_output, kap_thread, kap_visual_surface
    global pending_kap_path, pending_kap_name
    try:
        kap_path = Path(kap_path)
        if not skip_update_check:
            status = register_kap_app(kap_path, force_update=False)
            if status == 'needs_update':
                # Same name already installed from another file → ask user
                pending_kap_path = kap_path
                pending_kap_name = kap_path.stem
                app_actual = 'kap_update_confirm'
                reset_scroll()
                return

        toast(tr('kap_install'), 1200)
        code_content = kap_path.read_text(encoding='utf-8')
        tree = ast.parse(code_content)
        
        librerias_visuales = {'pygame', 'tkinter', 'turtle', 'pyqt5', 'pyqt6', 'customtkinter', 'pyside2', 'pyside6', 'kivy'}
        tiene_visuales = False

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split('.')[0].lower() in librerias_visuales:
                        tiene_visuales = True
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split('.')[0].lower() in librerias_visuales:
                    tiene_visuales = True

        if tiene_visuales:
            kap_terminal_active = False
            toast(tr('kap_success'), 2000)
            app_actual = 'kap_visual_app'
            reset_scroll()

            def run_visual_script():
                global kap_visual_surface
                try:
                    surf = pygame.Surface((ANCHO, ALTO - 100))
                    surf.fill((36, 38, 48))
                    kap_visual_surface = surf
                    namespace = {
                        '__name__': '__main__',
                        'screen': surf,
                        'canvas': surf,
                        'ANCHO': ANCHO,
                        'ALTO': ALTO - 100
                    }
                    exec(code_content, namespace)
                except Exception as ex:
                    try:
                        if kap_visual_surface is not None:
                            f = pygame.font.SysFont('notosans,arial', 16)
                            txt = f.render(str(ex)[:50], True, (231, 76, 60))
                            kap_visual_surface.blit(txt, (20, 40))
                    except Exception:
                        pass

            threading.Thread(target=run_visual_script, daemon=True).start()
        else:
            kap_terminal_active = True
            kap_terminal_output = [
                f"> Loading package: {kap_path.name}",
                "> No visual libraries detected.",
                "> Running in interactive terminal mode..."
            ]
            app_actual = 'kap_terminal'
            reset_scroll()

            def run_script():
                global kap_waiting_input, kap_input_result
                
                def custom_input(prompt=""):
                    global kap_waiting_input, kap_input_result
                    kap_input_result = None
                    kap_waiting_input = True
                    
                    if prompt:
                        kap_terminal_output.append(prompt)
                    
                    open_keyboard('text', '', prompt or "Input:", on_kap_input_received)
                    
                    while kap_waiting_input:
                        pygame.time.delay(100)
                        
                    return kap_input_result

                class TerminalRedirector:
                    def write(self, text):
                        if text.strip():
                            for line in text.splitlines():
                                kap_terminal_output.append(line)
                                if len(kap_terminal_output) > 60:
                                    kap_terminal_output.pop(0)
                    def flush(self):
                        pass

                sys.stdout = TerminalRedirector()
                sys.stderr = TerminalRedirector()

                try:
                    namespace = {'__name__': '__main__', 'input': custom_input}
                    exec(code_content, namespace)
                except Exception as ex:
                    kap_terminal_output.append(f"Error: {str(ex)}")
                finally:
                    sys.stdout = sys.__stdout__
                    sys.stderr = sys.__stderr__

            kap_thread = threading.Thread(target=run_script, daemon=True)
            kap_thread.start()

    except SyntaxError as e:
        toast(tr('kap_error'), 2000)
    except Exception as e:
        toast(tr('cannot'), 2000)


def on_kap_input_received(val):
    global kap_waiting_input, kap_input_result
    kap_input_result = val
    kap_terminal_output.append(f"> {val}")
    kap_waiting_input = False


def draw_kap_terminal():
    """Dibuja la terminal interactiva con soporte para teclado virtual."""
    canvas.fill(NEGRO)
    status()
    draw_text("KINETIX TERMINAL MODE", 20, 45, fuente15, VERDE)
    
    max_lineas = 11 if keyboard else 20
    lineas_visibles = kap_terminal_output[-max_lineas:]
    
    y = 75
    for line in lineas_visibles:
        draw_text(line[:55], 20, y, fuente15, VERDE)
        y += 22
        
    draw_text("Toca atrás o el botón home para salir.", 20, ALTO - 75, fuente15, GRIS)
    home_bar()


def draw_kap_visual_app():
    """Dibuja la interfaz visual de la app .kap ejecutada."""
    global kap_visual_surface
    canvas.fill(FONDO_APP)
    top("KAP App (Visual)", True)
    
    if kap_visual_surface is not None:
        try:
            canvas.blit(kap_visual_surface, (0, 90))
        except Exception:
            draw_text("Error al dibujar la app visual", 200, 250, fuente15, ROJO, True)
    else:
        draw_text("Cargando interfaz visual...", 200, 250, fuente15, GRIS_CLARO, True)
        
    home_bar()


def save_notes_file(name):
    global notes_path
    if not name:
        return
    if '.' not in Path(name).name:
        name+='.txt'
    p=(explorer_dir/name).resolve()
    if safe_main_path(p):
        p.write_text(notes_text,encoding='utf-8')
        notes_path=p
        toast(tr('saved'))
        app_actual='notes'


def reset_scroll():
    global scroll_y
    scroll_y=0


def scroll_by(d,maxv=500):
    global scroll_y
    scroll_y=max(0,min(maxv,scroll_y+d))


def draw_gallery():
    global gallery_mode, gallery_selected_image
    canvas.fill(FONDO_APP)
    files=[
        p for p in GALLERY_DIR.iterdir()
        if p.suffix.lower() in FORMATOS_SOPORTADOS['imagenes']
    ] if GALLERY_DIR.exists() else []

    if gallery_mode=='grid':
        top(tr('gallery'),True)
        if not files:
            draw_text(tr('gallery_empty'),200,300,fuente19,GRIS,True)
        else:
            cols=3
            thumb_w=110
            thumb_h=90
            margin_x=20
            spacing=15
            start_y=90-scroll_y
            for i, p in enumerate(files):
                r=i%cols
                c=i//cols
                x=margin_x+r*(thumb_w+spacing)
                y=start_y+c*(thumb_h+spacing)
                if -thumb_h<y<ALTO:
                    pygame.draw.rect(canvas,GRIS_OSCURO,(x,y,thumb_w,thumb_h),border_radius=8)
                    try:
                        im=pygame.image.load(str(p)).convert()
                        im=pygame.transform.smoothscale(im,(thumb_w-6,thumb_h-6))
                        canvas.blit(im,(x+3,y+3))
                    except:
                        draw_text('Error',x+thumb_w//2,y+thumb_h//2,fuente15,ROJO,True)
    elif gallery_mode=='detail' and gallery_selected_image:
        canvas.fill(NEGRO)
        try:
            im=pygame.image.load(str(gallery_selected_image)).convert()
            iw,ih=im.get_size()
            max_w,max_h=ANCHO,ALTO-100
            scale=min(max_w/iw,max_h/ih)
            nw,nh=int(iw*scale),int(ih*scale)
            im=pygame.transform.smoothscale(im,(nw,nh))
            ix=(ANCHO-nw)//2
            iy=60+((ALTO-60-nh)//2)
            canvas.blit(im,(ix,iy))
        except:
            draw_text('Error cargando imagen',ANCHO//2,ALTO//2,fuente19,ROJO,True)

        pygame.draw.rect(canvas,BARRA,(0,0,ANCHO,50))
        pygame.draw.polygon(canvas,GRIS_CLARO,[(25,25),(35,17),(35,33)])
        pygame.draw.rect(canvas,GRIS_CLARO,(33,22,10,6))
        try:
            mtime=os.path.getmtime(gallery_selected_image)
            dt_str=datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        except:
            dt_str='Fecha desconocida'
        draw_text(dt_str,ANCHO//2+15,25,fuente15,GRIS_CLARO,True)

    home_bar()


def safe_calc(expr):
    allowed={
        ast.Add:operator.add,
        ast.Sub:operator.sub,
        ast.Mult:operator.mul,
        ast.Div:operator.truediv,
        ast.Mod:operator.mod,
        ast.Pow:operator.pow,
        ast.USub:operator.neg
    }
    def ev(n):
        if isinstance(n,ast.Expression):
            return ev(n.body)
        if isinstance(n,ast.Constant) and isinstance(n.value,(int,float)):
            return n.value
        if isinstance(n,ast.BinOp) and type(n.op) in allowed:
            return allowed[type(n.op)](ev(n.left),ev(n.right))
        if isinstance(n,ast.UnaryOp) and type(n.op) in allowed:
            return allowed[type(n.op)](ev(n.operand))
        raise ValueError('Invalid expression')
    return ev(ast.parse(expr,mode='eval'))


def draw_calculator():
    canvas.fill(FONDO_APP)
    top(tr('calculator'),True)
    draw_text(calculator_text or tr('calculator_help'),200,100,fuente19,GRIS_CLARO,True)
    keys=['7','8','9','/','4','5','6','*','1','2','3','-','0','.','=','+','C']
    for i,k in enumerate(keys):
        x=20+(i%4)*92
        y=145+(i//4)*55
        button(pygame.Rect(x,y,82,45),k,AZUL if k=='=' else GRIS_OSCURO)
    home_bar()


def draw_game():
    canvas.fill(FONDO_APP)
    top(tr('games'),True)
    draw_text(tr('catch'),200,90,fuente19,GRIS_CLARO,True)
    draw_text(f'{tr("score")}: {game_score}',15,115,fuente15,GRIS)
    pygame.draw.circle(canvas,ROJO,(game_x,game_y),22)
    draw_text('Toca el círculo',200,550,fuente15,GRIS,True)
    home_bar()


def prepare_error(exc):
    global error_info,app_actual
    tb=traceback.format_exc()
    error_info={
        'file':str(Path(__file__).resolve()),
        'problem':str(exc),
        'traceback':tb
    }
    try:
        (LOG_DIR/'last_kx8.log').write_text(f'KX 8\n{tb}',encoding='utf-8')
    except:
        pass
    app_actual='error'
    reset_scroll()


def draw_error():
    canvas.fill((45,5,8))
    draw_text('KX 8',200,60,fuente40,ROJO,True)
    draw_text(tr('python_error'),200,105,fuente23,GRIS_CLARO,True)
    if error_info:
        draw_text(f'{tr("file_caused")}: {error_info["file"]}',10,140,fuente15,GRIS_CLARO)
        draw_text(f'{tr("problem")}: {error_info["problem"]}',10,165,fuente15,GRIS_CLARO)
        y=205-scroll_y
        for line in error_info['traceback'].splitlines():
            draw_text(line[:62],10,y,fuente15,(245,190,190))
            y+=17
    button(pygame.Rect(10,535,115,42),tr('repair'),VIOLETA)
    button(pygame.Rect(135,535,115,42),tr('restart'),AZUL)
    button(pygame.Rect(260,535,130,42),tr('continue'),VERDE)


def lock_success():
    global app_actual,lock_mode,pin_attempts,pin_locked_until,lock_pin_entry
    pin_attempts=0
    pin_locked_until=0
    lock_mode='none'
    lock_pin_entry=''
    app_actual='desktop'


def after_slide_unlock():
    global app_actual,lock_mode,lock_pin_entry
    if pin_enabled and len(pin_hash)==4 and pin_hash.isdigit():
        lock_mode='pin'
        lock_pin_entry=''
        app_actual='lock'
    else:
        lock_success()


def check_pin(p):
    global pin_attempts,pin_locked_until
    if pygame.time.get_ticks()<pin_locked_until:
        return False
    if p==pin_hash:
        lock_success()
        return True
    pin_attempts+=1
    toast(tr('wrong_pin'),1000)
    if pin_attempts>=5:
        pin_attempts=0
        pin_locked_until=pygame.time.get_ticks()+60000
    return False


def enter_pin_keyboard():
    open_keyboard('numeric','',tr('enter_pin'),check_pin)


def lock_device():
    global app_actual,lock_mode,lock_pin_entry,lock_gesture_start,lock_gesture_y
    lock_mode='slide'
    lock_pin_entry=''
    lock_gesture_start=None
    lock_gesture_y=0
    app_actual='lock'
    reset_scroll()


def choose_new_pin_after_current(_=None):
    open_keyboard('numeric','',tr('new_pin'),new_pin_first)


def new_pin_first(v):
    if len(v)!=4 or not v.isdigit():
        toast(tr('pin_invalid'))
        return
    open_keyboard('numeric','',tr('repeat_pin'),lambda v2:finish_new_pin(v,v2))


def finish_new_pin(a,b):
    if a!=b:
        toast(tr('pin_bad'))
        return
    set_pin(a)
    toast(tr('pin_ok'))
    app_actual='pin'


def verify_pin_for_factory(v):
    global app_actual
    if v == pin_hash:
        app_actual = 'factory_confirm'
    else:
        toast(tr('wrong_pin'))


def request_current_pin_for_pin_section():
    if pin_enabled:
        open_keyboard('numeric','',tr('pin_current'),lambda v:verify_current_for_change(v))
    else:
        choose_new_pin_after_current()


def verify_current_for_change(v):
    if v==pin_hash:
        choose_new_pin_after_current()
    else:
        toast(tr('wrong_pin'))


def factory_confirm_draw():
    canvas.fill(FONDO_APP)
    top(tr('factory'), True)
    draw_text(tr('factory_options'), 200, 95, fuente19, GRIS_CLARO, True)
    # 1. Reset with backup
    button(pygame.Rect(25, 140, 350, 55), tr('reset_with_backup'), AZUL, font=fuente15)
    # 2. Reset without backup
    button(pygame.Rect(25, 210, 350, 55), tr('reset_no_backup'), ROJO, font=fuente15)
    # 3. Cancel
    button(pygame.Rect(25, 280, 350, 55), tr('cancel'), GRIS_OSCURO, font=fuente15)
    home_bar()


def kap_update_confirm_draw():
    canvas.fill(FONDO_APP)
    top(tr('kap_update_title'), True)
    name = pending_kap_name or ''
    draw_text(name, 200, 120, fuente23, AZUL, True)
    # Multiline-ish message
    msg = tr('kap_update_ask')
    # Simple wrap by character count
    if len(msg) > 36:
        mid = len(msg) // 2
        # split near space
        sp = msg.rfind(' ', 0, mid + 8)
        if sp < 10:
            sp = mid
        draw_text(msg[:sp].strip(), 200, 175, fuente15, GRIS_CLARO, True)
        draw_text(msg[sp:].strip(), 200, 198, fuente15, GRIS_CLARO, True)
    else:
        draw_text(msg, 200, 180, fuente15, GRIS_CLARO, True)
    button(pygame.Rect(45, 250, 140, 55), tr('yes'), VERDE)
    button(pygame.Rect(215, 250, 140, 55), tr('no'), GRIS_OSCURO)
    home_bar()


def confirm_kap_update(do_update):
    """
    Sí → sobrescribe el .kap instalado en el dispositivo con el nuevo, actualiza
    icono/acceso directo y ejecuta la versión instalada.
    No → no modifica el instalado; solo ejecuta el archivo que acabas de abrir.
    """
    global pending_kap_path, pending_kap_name, app_actual
    path = pending_kap_path
    name = pending_kap_name
    pending_kap_path = None
    pending_kap_name = None
    if path is None:
        app_actual = 'files'
        return
    if do_update:
        register_kap_app(path, force_update=True)
        toast(tr('kap_updated'), 1500)
        # Ejecutar el .kap ya instalado (ruta del acceso directo)
        existing = find_desktop_app_by_name(name) if name else None
        run_path = Path(existing['path']) if existing and existing.get('path') else path
        inspect_and_run_kap_package(run_path, skip_update_check=True)
    else:
        toast(tr('kap_not_updated'), 1500)
        inspect_and_run_kap_package(path, skip_update_check=True)


def handle_home(x,y):
    global app_actual,keyboard,scroll_y,gallery_mode,kap_terminal_active,kap_waiting_input
    # Durante el asistente inicial el Home está bloqueado por completo
    if setup_mode:
        return True  # consumir el toque, no salir
    if y>=ALTO-62 and abs(x-200)<50:
        keyboard=None
        app_actual='desktop'
        gallery_mode='grid'
        kap_terminal_active=False
        kap_waiting_input=False
        reset_scroll()
        return True
    return False


def set_language(lang):
    global idioma, app_actual, setup_mode
    idioma = lang
    save_json(LANG_FILE, {'language': lang})
    toast('Language saved' if lang == 'en' else 'Idioma guardado')
    if setup_mode:
        # Tras idioma → fecha y hora (DT_FILE solo se escribe al terminar)
        app_actual = 'datetime'
    else:
        app_actual = 'system'


def finish_setup():
    """Termina el asistente inicial y deja usar el teléfono con normalidad."""
    global setup_mode, app_actual
    save_datetime()
    setup_mode = False
    app_actual = 'desktop'
    toast(tr('saved'), 1200)


def start_setup_if_needed():
    global app_actual, setup_mode
    if not LANG_FILE.exists():
        setup_mode = True
        app_actual = 'language'
        return
    if not DT_FILE.exists():
        setup_mode = True
        app_actual = 'datetime'
        return
    setup_mode = False
    app_actual = 'desktop'


def handle_event(e):
    global app_actual,pantalla_anterior,ajuste_seccion
    global selected_path,explorer_mode,explorer_dir
    global notes_text,notes_path,calculator_text
    global game_x,game_y,game_score
    global lock_gesture_start,lock_gesture_y
    global drag_active,drag_start_y,drag_start_scroll
    global drag_moved,scroll_y,last_finger_ms
    global date_drag_field,date_drag_last_y
    global last_touch_ms,lock_pin_entry

    now=pygame.time.get_ticks()

    if e.type==pygame.QUIT:
        power_off()

    if e.type==pygame.KEYDOWN and app_actual!='lock':
        if keyboard:
            if e.key==pygame.K_BACKSPACE:
                keyboard['value']=keyboard['value'][:-1]
            elif e.key==pygame.K_RETURN:
                finish_keyboard()
            elif e.key==pygame.K_SPACE:
                keyboard['value']+=' '
            elif e.unicode and e.unicode.isprintable():
                keyboard['value']+=e.unicode
            return

    if e.type==pygame.FINGERDOWN:
        last_finger_ms=now
        last_touch_ms=now
        x,y=posicion_logica((e.x*pantalla.get_width(),e.y*pantalla.get_height()))
        if app_actual=='lock':
            if lock_mode=='slide':
                lock_gesture_start=y
                lock_gesture_y=y
                drag_active=True
                drag_moved=False
            else:
                drag_active=False
                drag_moved=False
        else:
            drag_active=True
            drag_start_y=y
            drag_start_scroll=scroll_y
            drag_moved=False
            if app_actual=='datetime':
                fields=['day','month','year','hour','minute']
                date_drag_field=fields[int((y-90)//58)] if 90<=y<380 else None
                date_drag_last_y=y
        return

    if e.type==pygame.FINGERMOTION:
        x,y=posicion_logica((e.x*pantalla.get_width(),e.y*pantalla.get_height()))
        if app_actual=='lock' and lock_mode=='slide' and lock_gesture_start is not None:
            lock_gesture_y=y
            if abs(y-lock_gesture_start)>8:
                drag_moved=True
            return
        if app_actual=='datetime' and drag_active and date_drag_field and abs(y-date_drag_last_y)>=18:
            step=-1 if y>date_drag_last_y else 1
            adjust_field(date_drag_field,step)
            date_drag_last_y=y
            drag_moved=True
        if drag_active:
            dy=y-drag_start_y
            if abs(dy)>4:
                drag_moved=True
                scroll_y=max(0,min(800,drag_start_scroll-dy))
        return

    if e.type==pygame.FINGERUP:
        last_touch_ms=now
        x,y=posicion_logica((e.x*pantalla.get_width(),e.y*pantalla.get_height()))
        if app_actual=='lock' and lock_mode=='slide':
            if lock_gesture_start is not None and lock_gesture_start-y>=50:
                after_slide_unlock()
            lock_gesture_start=None
            lock_gesture_y=0
            drag_active=False
            drag_moved=False
            return
        if app_actual=='lock' and lock_mode=='pin':
            if not drag_moved:
                process_click(x,y)
            drag_active=False
            return
        if not drag_moved:
            if not handle_home(x,y):
                process_click(x,y)
        lock_gesture_start=None
        drag_active=False
        return

    if e.type in (pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP,pygame.MOUSEMOTION) and now-last_touch_ms<300:
        return

    if e.type==pygame.MOUSEBUTTONDOWN:
        x,y=posicion_logica(e.pos)
        if e.button==1:
            if app_actual=='lock' and lock_mode=='slide':
                lock_gesture_start=y
                lock_gesture_y=y
                drag_active=True
                drag_moved=False
                return
            drag_active=True
            drag_start_y=y
            drag_start_scroll=scroll_y
            drag_moved=False
            if app_actual=='datetime':
                fields=['day','month','year','hour','minute']
                date_drag_field=fields[int((y-90)//58)] if 90<=y<380 else None
                date_drag_last_y=y
            if handle_home(x,y):
                return
        elif e.button in (4,5):
            scroll_by(-45 if e.button==4 else 45)
        return

    if e.type==pygame.MOUSEMOTION and drag_active:
        x,y=posicion_logica(e.pos)
        dy=y-drag_start_y
        if app_actual=='lock' and lock_mode=='slide':
            lock_gesture_y=y
            if lock_gesture_start is not None and abs(y-lock_gesture_start)>8:
                drag_moved=True
            return
        if app_actual=='datetime' and date_drag_field and abs(y-date_drag_last_y)>=18:
            step=-1 if y>date_drag_last_y else 1
            adjust_field(date_drag_field,step)
            date_drag_last_y=y
            drag_moved=True
        if abs(dy)>4:
            drag_moved=True
            scroll_y=max(0,min(800,drag_start_scroll-dy))
        return

    if e.type==pygame.MOUSEBUTTONUP and e.button==1:
        x,y=posicion_logica(e.pos)
        if app_actual=='lock' and lock_mode=='slide':
            if lock_gesture_start is not None and lock_gesture_start-y>=50:
                after_slide_unlock()
            lock_gesture_start=None
            lock_gesture_y=0
            drag_active=False
            drag_moved=False
            return
        if app_actual=='lock' and lock_mode=='pin':
            if not drag_moved:
                process_click(x,y)
            drag_active=False
            return
        if not drag_moved:
            process_click(x,y)
        drag_active=False
        lock_gesture_start=None
        date_drag_field=None


def process_click(x,y):
    global app_actual,pantalla_anterior,ajuste_seccion
    global explorer_mode,explorer_dir,selected_path
    global notes_text,notes_path,calculator_text
    global game_x,game_y,game_score,lock_pin_entry
    global gallery_mode, gallery_selected_image, kap_terminal_active, kap_waiting_input
    global pending_kap_path, pending_kap_name

    if keyboard:
        keyboard_key(x,y)
        return

    if app_actual=='desktop':
        for k, n, ax, ay, path, _icon in get_desktop_app_positions():
            if pygame.Rect(ax, ay, 80, 80).collidepoint(x, y):
                if path:
                    p = Path(path)
                    if p.exists():
                        inspect_and_run_kap_package(p)
                    else:
                        toast(tr('cannot'))
                    return
                if k == 'settings':
                    app_actual = 'settings'
                elif k == 'games':
                    app_actual = 'game'
                elif k == 'gallery':
                    app_actual = 'gallery'
                    gallery_mode = 'grid'
                    reset_scroll()
                elif k == 'calculator':
                    app_actual = 'calculator'
                elif k == 'notes':
                    app_actual = 'notes'
                elif k == 'files':
                    app_actual = 'files'
                    explorer_mode = 'normal'
                    explorer_dir = MAIN_DIR
                    selected_path = None
                    reset_scroll()
                elif k == 'power':
                    app_actual = 'power'
                return

    elif app_actual=='settings':
        if pygame.Rect(25,85,350,62).collidepoint(x,y):
            app_actual='datetime'
        elif pygame.Rect(25,160,350,62).collidepoint(x,y):
            app_actual='system'
        elif pygame.Rect(25,235,350,62).collidepoint(x,y):
            app_actual='pin'

    elif app_actual=='datetime':
        if not setup_mode and pygame.Rect(12, 40, 72, 32).collidepoint(x, y):
            app_actual = 'settings'
            return
        if setup_mode and pygame.Rect(40, 460, 320, 50).collidepoint(x, y):
            finish_setup()
            return
        for i, k in enumerate(['day', 'month', 'year', 'hour', 'minute']):
            if pygame.Rect(25, 90 + i * 58, 350, 45).collidepoint(x, y):
                adjust_field(k, 1)
                return

    elif app_actual=='system':
        if pygame.Rect(12,40,72,32).collidepoint(x,y):
            app_actual='settings'
        elif pygame.Rect(25,90,350,55).collidepoint(x,y):
            app_actual='system_info'
            reset_scroll()
        elif pygame.Rect(25,155,350,55).collidepoint(x,y):
            app_actual='language'
        elif pygame.Rect(25, 220, 350, 55).collidepoint(x, y):
            if pin_enabled and pin_hash:
                open_keyboard('numeric', '', tr('enter_pin_factory'), verify_pin_for_factory)
            else:
                app_actual = 'factory_confirm'

    elif app_actual=='system_info':
        if pygame.Rect(12,40,72,32).collidepoint(x,y):
            app_actual='system'

    elif app_actual=='language':
        if not setup_mode and pygame.Rect(12, 40, 72, 32).collidepoint(x, y):
            app_actual = 'system'
        elif pygame.Rect(30, 100, 340, 65).collidepoint(x, y):
            set_language('en')
        elif pygame.Rect(30, 180, 340, 65).collidepoint(x, y):
            set_language('es')

    elif app_actual=='pin':
        if pygame.Rect(12,40,72,32).collidepoint(x,y):
            app_actual='settings'
        elif pygame.Rect(30,145,340,55).collidepoint(x,y):
            request_current_pin_for_pin_section()
        elif pin_enabled and pygame.Rect(30,215,340,55).collidepoint(x,y):
            if pin_enabled:
                open_keyboard('numeric','',tr('pin_current'),lambda v:disable_if_correct(v))

    elif app_actual=='factory_confirm':
        if pygame.Rect(12, 40, 72, 32).collidepoint(x, y):
            app_actual = 'system'
        elif pygame.Rect(25, 140, 350, 55).collidepoint(x, y):
            reset_user(with_backup=True)
        elif pygame.Rect(25, 210, 350, 55).collidepoint(x, y):
            reset_user(with_backup=False)
        elif pygame.Rect(25, 280, 350, 55).collidepoint(x, y):
            app_actual = 'system'

    elif app_actual=='kap_update_confirm':
        if pygame.Rect(12, 40, 72, 32).collidepoint(x, y):
            # Cancel: do not run, do not update
            pending_kap_path = None
            pending_kap_name = None
            app_actual = 'files'
        elif pygame.Rect(45, 250, 140, 55).collidepoint(x, y):
            confirm_kap_update(True)
        elif pygame.Rect(215, 250, 140, 55).collidepoint(x, y):
            confirm_kap_update(False)

    elif app_actual=='power':
        if pygame.Rect(12,40,72,32).collidepoint(x,y):
            app_actual='desktop'
        elif pygame.Rect(35,110,330,60).collidepoint(x,y):
            lock_device()
        elif pygame.Rect(35,185,330,60).collidepoint(x,y):
            restart_process()
        elif pygame.Rect(35,260,330,60).collidepoint(x,y):
            power_off()

    elif app_actual=='notes':
        if pygame.Rect(8,40,90,34).collidepoint(x,y):
            app_actual='files'
            explorer_mode='notes_open'
            explorer_dir=MAIN_DIR
            selected_path=None
            reset_scroll()
        elif pygame.Rect(108,40,90,34).collidepoint(x,y):
            if notes_path:
                notes_path.write_text(notes_text,encoding='utf-8')
                toast(tr('saved'))
            else:
                app_actual='files'
                explorer_mode='notes_save'
                explorer_dir=MAIN_DIR
                selected_path=None
                reset_scroll()
        elif pygame.Rect(18,115,364,330).collidepoint(x,y):
            open_keyboard('text',notes_text,tr('notes'),lambda v:set_notes(v))

    elif app_actual=='files':
        if pygame.Rect(8,40,72,32).collidepoint(x,y):
            if explorer_dir!=MAIN_DIR:
                explorer_dir=explorer_dir.parent
                reset_scroll()
            else:
                app_actual=('notes' if explorer_mode.startswith('notes_') else 'desktop')
            return
        if explorer_mode=='notes_save' and pygame.Rect(15,455,240,40).collidepoint(x,y):
            open_keyboard('text','',tr('type_name'),save_notes_file)
            return
        if explorer_mode=='notes_save' and pygame.Rect(265,455,120,40).collidepoint(x,y):
            if selected_path:
                save_notes_file(selected_path.name)
            return
        if not drag_moved:
            select_explorer_at(x, y)
            if selected_path and selected_path.is_file():
                suf = selected_path.suffix.lower()
                if suf in FORMATOS_SOPORTADOS['paquetes']:
                    inspect_and_run_kap_package(selected_path)
                    return
                if suf in FORMATOS_SOPORTADOS['saves']:
                    restore_from_save(selected_path)
                    return
        if explorer_mode=='notes_open' and selected_path and selected_path.is_file() and pygame.Rect(280,455,100,40).collidepoint(x,y):
            load_note_selected()

    elif app_actual=='gallery':
        if gallery_mode=='grid':
            if pygame.Rect(12,40,72,32).collidepoint(x,y):
                app_actual='desktop'
            else:
                files=[
                    p for p in GALLERY_DIR.iterdir()
                    if p.suffix.lower() in FORMATOS_SOPORTADOS['imagenes']
                ] if GALLERY_DIR.exists() else []
                cols=3
                thumb_w=110
                thumb_h=90
                margin_x=20
                spacing=15
                start_y=90-scroll_y
                for i, p in enumerate(files):
                    r=i%cols
                    c=i//cols
                    rx=margin_x+r*(thumb_w+spacing)
                    ry=start_y+c*(thumb_h+spacing)
                    if pygame.Rect(rx,ry,thumb_w,thumb_h).collidepoint(x,y):
                        gallery_selected_image=p
                        gallery_mode='detail'
                        break
        elif gallery_mode=='detail':
            if pygame.Rect(10,10,40,30).collidepoint(x,y):
                gallery_mode='grid'
                gallery_selected_image=None

    elif app_actual=='calculator':
        if pygame.Rect(12,40,72,32).collidepoint(x,y):
            app_actual='desktop'
            return
        keys=['7','8','9','/','4','5','6','*','1','2','3','-','0','.','=','+','C']
        for i,k in enumerate(keys):
            r=pygame.Rect(20+(i%4)*92,145+(i//4)*55,82,45)
            if r.collidepoint(x,y):
                if k=='C':
                    calculator_text=''
                elif k=='=':
                    try:
                        calculator_text=str(safe_calc(calculator_text))
                    except:
                        calculator_text='Error'
                else:
                    calculator_text+=k

    elif app_actual=='game':
        if pygame.Rect(12,40,72,32).collidepoint(x,y):
            app_actual='desktop'
            return
        if math.hypot(x-game_x,y-game_y)<30:
            game_score+=1
            game_x=random.randint(30,370)
            game_y=random.randint(150,500)

    elif app_actual=='kap_visual_app':
        if pygame.Rect(12,40,72,32).collidepoint(x,y):
            app_actual='files'
            return

    elif app_actual=='kap_terminal':
        if pygame.Rect(12,40,72,32).collidepoint(x,y):
            kap_terminal_active=False
            kap_waiting_input=False
            app_actual='files'
            return

    elif app_actual=='error':
        if pygame.Rect(10,535,115,42).collidepoint(x,y):
            ensure_structure()
            restart_process()
        elif pygame.Rect(135,535,115,42).collidepoint(x,y):
            restart_process()
        elif pygame.Rect(260,535,130,42).collidepoint(x,y):
            app_actual='desktop'
            error_info=None

    elif app_actual=='lock':
        if lock_mode=='pin' and pygame.time.get_ticks()>=pin_locked_until:
            keys=['1','2','3','4','5','6','7','8','9','0']
            for i,n in enumerate(keys):
                row=i//3
                col=i%3
                if i==9:
                    r=pygame.Rect(150,500,100,48)
                else:
                    r=pygame.Rect(70+col*90,275+row*65,70,50)
                if r.collidepoint(x,y):
                    if len(lock_pin_entry)<4:
                        lock_pin_entry+=n
                        if len(lock_pin_entry)==4:
                            if not check_pin(lock_pin_entry):
                                lock_pin_entry=''
                    return


def set_date_field(k,v):
    try:
        n=int(v)
    except:
        return
    limits={
        'day':(1,31),
        'month':(1,12),
        'year':(2026,2126),
        'hour':(0,23),
        'minute':(0,59)
    }
    lo,hi=limits[k]
    if lo<=n<=hi:
        virtual[k]=n
        save_datetime()
    else:
        toast('Invalid value' if idioma=='en' else 'Valor no válido')


def set_notes(v):
    global notes_text
    notes_text=v


def disable_if_correct(v):
    if v==pin_hash:
        disable_pin()
    else:
        toast(tr('wrong_pin'))


def load_note_selected():
    global notes_text,notes_path,app_actual
    try:
        if selected_path and safe_main_path(selected_path):
            if selected_path.suffix.lower() in FORMATOS_SOPORTADOS['imagenes']:
                toast(tr('cannot'))
                return
            notes_text=selected_path.read_text(encoding='utf-8')
            notes_path=selected_path
            app_actual='notes'
            toast(tr('saved'))
    except Exception as e:
        prepare_error(e)


def draw_all():
    if app_actual=='desktop':
        draw_desktop()
    elif app_actual=='settings':
        draw_settings()
    elif app_actual=='datetime':
        draw_datetime()
    elif app_actual=='system':
        draw_system()
    elif app_actual=='system_info':
        draw_system_info()
    elif app_actual=='language':
        draw_language()
    elif app_actual=='pin':
        draw_pin()
    elif app_actual=='factory_confirm':
        factory_confirm_draw()
    elif app_actual=='kap_update_confirm':
        kap_update_confirm_draw()
    elif app_actual=='power':
        draw_power()
    elif app_actual=='notes':
        draw_notes()
    elif app_actual=='files':
        draw_explorer(save_mode=explorer_mode=='notes_save')
    elif app_actual=='gallery':
        draw_gallery()
    elif app_actual=='calculator':
        draw_calculator()
    elif app_actual=='game':
        draw_game()
    elif app_actual=='kap_visual_app':
        draw_kap_visual_app()
    elif app_actual=='kap_terminal':
        draw_kap_terminal()
    elif app_actual=='lock':
        draw_lock()
    elif app_actual=='error':
        draw_error()

    if keyboard and app_actual not in ('lock','error'):
        keyboard_draw()

    if toast_text and pygame.time.get_ticks()<toast_until:
        r=pygame.Rect(45,ALTO-105,310,40)
        pygame.draw.rect(canvas,(10,12,16),r,border_radius=18)
        draw_text(toast_text,200,r.centery,fuente15,GRIS_CLARO,True)
    elif toast_text:
        pass


def boot():
    global idioma
    canvas.fill(NEGRO)
    draw_text('KINETIX', 200, 270, fuente40, GRIS_CLARO, True)
    draw_text('1.0', 200, 320, fuente23, GRIS, True)
    presentar()

    pygame.time.delay(3000)

    load_config()
    load_pin()
    start_setup_if_needed()

    # Solo bloquear si ya terminó el setup
    if app_actual == 'desktop' and not setup_mode:
        lock_device()


def main():
    global running
    boot()
    while running:
        try:
            tick_clock()
            for e in pygame.event.get():
                handle_event(e)
            draw_all()
            presentar()
            pygame.time.Clock().tick(FPS)
        except SystemExit:
            raise
        except Exception as exc:
            prepare_error(exc)


if __name__=='__main__':
    try:
        main()
    except SystemExit:
        pass
    except Exception as exc:
        prepare_error(exc)
        while True:
            try:
                for e in pygame.event.get():
                    if e.type==pygame.QUIT:
                        pygame.quit()
                        raise SystemExit
                    if e.type==pygame.MOUSEBUTTONDOWN:
                        x,y=posicion_logica(e.pos)
                        if pygame.Rect(135,535,115,42).collidepoint(x,y):
                            restart_process()
                draw_error()
                presentar()
                pygame.time.Clock().tick(FPS)
            except SystemExit:
                raise
            except Exception:
                pygame.time.delay(100)
