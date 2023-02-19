"""
The main engine instance used to run programs using pyengine :)
"""
import ctypes
import math
import os.path
import sys
import time
import pygame
from pygame import gfxdraw as gx
from typing import Optional, Union

if __package__ is None or __package__ == '':
    import Scene
    import EngineLog
    from Constants import *
    from RenderObject import RenderObject
else:
    from . import Scene
    from . import EngineLog
    from .Constants import *
    from .RenderObject import RenderObject

""" ------------- ENGINE PRIVATE VARIABLES ----------- """
_m_e_IsInit: bool = False


def get_init() -> bool:
    """
    Has the engine been initialised?
    :return:
    """
    return _m_e_IsInit


def _set_init(_init: bool) -> None:
    """
    Sets the engine as having been initialised
    :param _init:
    :return:
    """
    global _m_e_IsInit
    _m_e_IsInit = _init


_m_eIsRunning: bool = False


# Only the engine should be able to set wether it is running
def _set_running(running: bool) -> None:
    """
    Sets the engine as having started/ended its lifecycle
    :param running: should run
    :return:
    """
    global _m_eIsRunning
    _m_eIsRunning = running


def get_running() -> bool:
    """
    Checks to see if the engine.Init() function has been called
    :return: wether the engine is running
    """
    return _m_eIsRunning


_m_eIsDebug: bool = False


def get_engine_debugmode() -> bool:
    """
    Determines wether the engine is running in debug or build mode
    :return: engine debug value
    """
    return _m_eIsDebug


def set_engine_debugmode(debugmode: bool) -> None:
    """
    Sets wether the engine is running in debug or build mode. Cannot be used if the engine is running
    :param debugmode: should the engine debug?
    :return: None
    """
    _check_safe()
    global _m_eIsDebug
    _m_eIsDebug = debugmode


_m_eKeyCallback: list = []


def add_key_callback(newfunct) -> None:
    """
    Adds a callback function that is called whenever a key event is registered. Takes an event as a parameter
    :param newfunct: callback function
    :return: None
    """
    global _m_eKeyCallback
    _m_eKeyCallback.append(newfunct)


def remove_key_callback(oldfunct) -> int:
    """
    Removes a key callback function
    :param oldfunct: pointer to function to be removed
    :return: Was the removal successful (0 if yes otherwise 1)
    """
    global _m_eKeyCallback
    if oldfunct in _m_eKeyCallback:
        _m_eKeyCallback.remove(oldfunct)
        return 0
    return 1


_m_eMouseCallback: list = []


def add_mouse_callback(newfunct) -> None:
    """
    Adds a callback function that is called whenever a mouse event is registered. Takes an event as a parameter
    :param newfunct: callback function
    :return: None
    """
    global _m_eMouseCallback
    _m_eMouseCallback.append(newfunct)


def remove_mouse_callback(oldfunct) -> int:
    """
    Removes a mouse callback function
    :param oldfunct: pointer to function to be removed
    :return: Was the removal successful (0 if yes otherwise 1)
    """
    global _m_eMouseCallback
    if oldfunct in _m_eKeyCallback:
        _m_eMouseCallback.remove(oldfunct)
        return 0
    return 1


_m_eTickrate: float = 60
_m_eTimePerTick: float = 1e3 / 60


def get_engine_tickrate() -> float:
    """
    Returns the number of steps the engine takes in a second
    :return: number opf ticks
    """
    return _m_eTickrate


def set_engine_tickrate(newTickrate: float) -> None:
    """
    Sets the number of steps the engine takes in a second. Can only be called before engine is running
    :param newTickrate: new tickrate. Values of 0 will be ignored retard :D
    :return: None
    """
    _check_safe()
    global _m_eTickrate, _m_eTimePerTick
    _m_eTickrate = newTickrate if newTickrate > 0 else _m_eTickrate
    _m_eTimePerTick = ticks_to_time(1)


_m_eTickbase: int = 0


def get_client_tickbase() -> int:
    """
    Gets the current total full steps the engine has taken
    :return: number of full steps
    """
    return _m_eTickbase


# There may be some situations we want to increase tickbase
def set_client_tickbase(newTickbase: int) -> None:
    """
    Sets the current client tickbase
    :param newTickbase: new tickbase value
    :return:
    """
    global _m_eTickbase
    _m_eTickbase = newTickbase


def step_client_tickbase(stepAmount: int) -> None:
    """
    Steps the current client tickbase by a given amount
    :param stepAmount: amount to step (neg or pos)
    :return: None
    """
    global _m_eTickbase
    _m_eTickbase += stepAmount


_m_eFPS: float = 0


def get_fps() -> float:
    """
    Gets the current frames rendered per second
    :return: fps
    """
    return _m_eFPS


_m_eTPS: float = 0


def get_tps() -> float:
    """
    Gets the current ticks per second (should always be equal to engine tickrate)
    :return: ticks per second
    """
    return _m_eTPS


_m_eCurrentScene: Optional[Scene.Scene] = None


def set_scene(newScene: Scene.Scene) -> None:
    """
    Sets the current scene which will be rendered and drawn
    :param newScene: new scene to be handled
    :return:
    """
    global _m_eCurrentScene
    _m_eCurrentScene = newScene


_m_eOverlays: list = []

_m_rResolution: tuple = (640, 480)


def set_resolution(newRes: tuple) -> None:
    """
    Sets the current window resolution
    :param newRes: tuple containing the (w, h) of the window
    :return: None
    """
    global _m_rResolution
    _m_rResolution = newRes if newRes[0] > 0 and newRes[1] > 0 else _m_rResolution


def get_resolution() -> tuple:
    return _m_rResolution


_m_rWindow: Optional[pygame.Surface] = None
_m_rQueue: list = []
_m_rPrevRect: Optional[pygame.Rect] = None

_m_rTextureBank: dict = {}
_m_rTextureCache: dict = {}
_m_rToCleanup: list = []

_m_rRenderFlags = 0


def _set_render_flag(render_flag: int, shouldSet: bool) -> None:
    """
    Sets one of the boolean render flags
    :param render_flag: which render flag to set (defined in Constants.py)
    :param shouldSet: wether to set or unset the flag
    :return: None
    """
    global _m_rRenderFlags
    if shouldSet:
        _m_rRenderFlags |= render_flag
        return
    _m_rRenderFlags &= ~render_flag


def _get_render_flag(render_flag: int) -> bool:
    """
    Gets the value of the render flag
    :param render_flag: render flag to get (defined in Constants.py)
    :return: value of render_flag
    """
    global _m_rRenderFlags
    return bool(_m_rRenderFlags & render_flag)


def set_fullscreen(shouldFullscreen: bool) -> None:
    _set_render_flag(RF_FULLSCREEN, shouldFullscreen)


def get_fullscreen() -> bool:
    return _get_render_flag(RF_FULLSCREEN)


def set_borderless(shouldBorderless: bool) -> None:
    _set_render_flag(RF_BORDERLESS, shouldBorderless)


def get_borderless() -> bool:
    return _get_render_flag(RF_BORDERLESS)


def set_vsync(shouldVsync: bool) -> None:
    _set_render_flag(RF_VSYNC, shouldVsync)


def get_vsync() -> bool:
    return _get_render_flag(RF_VSYNC)


_m_rLastRefresh: Optional[Union[tuple, str]] = None

_m_eEngineLogger: Optional[EngineLog.Logger] = None
_m_eClientLogger: Optional[EngineLog.Logger] = None


def get_client_logger() -> EngineLog.Logger:
    return _m_eClientLogger


_m_eIncludeSystems: list[tuple[callable, callable]] = []
_m_eSysNames: list[str] = []


def _render_nothing():
    pass


def add_system(name: str, callback_update: callable, callback_render=_render_nothing):
    _m_eIncludeSystems.append((callback_update, callback_render))
    _m_eSysNames.append(name)


def remove_system(name):
    index = _m_eSysNames.index(name)
    _m_eSysNames.remove(name)
    del _m_eIncludeSystems[index]


""" ------------------ ENGINE PRIVATE FUNCTIONS -----------------"""


def _raise_engine_error(message: str, isfatal=True) -> None:
    """
    Raises an engine error correctly depending on wether the engine is built in debug or release mode
    :param message: error log to print
    :return: None
    """
    if get_init():
        _m_eEngineLogger.error(message)
    # IF engine is in debug mode then print exception
    if get_engine_debugmode():
        raise Exception(message)
    elif isfatal:
        # else create a Windows error box and exit application
        ctypes.windll.user32.MessageBoxW(0, f"An engine error has occured: {message}", "Error!", 16)
        _set_running(False)


def _check_safe() -> None:
    """
    Used in setters for variables that cannot be changed during the engine's lifetime. Raises an engine error if this
    happens
    :return: None
    """
    if not get_running():
        return
    _raise_engine_error("Attempting to change engine variable while the engine is still running")


def _engine_combine_rect(rect1: Optional[pygame.Rect], rect2: Optional[pygame.Rect]) -> pygame.Rect:
    """
    Unionizes two pygame rectangles
    :param rect1: first rectangle (if none rect2 is returned)
    :param rect2: second rectangle (must be present)
    :return: Union of the two rectangles (or rect 2 if rect 1 is null)
    """
    if not rect1:
        return rect2
    if not rect2:
        return rect1
    mLeft = min(rect1.left, rect2.left)
    mTop = min(rect1.top, rect2.top)
    return pygame.Rect(mLeft, mTop, max(rect1.right, rect2.right) - mLeft, max(rect1.bottom, rect2.bottom) - mTop)


def _engine_quit():
    _m_eEngineLogger.info("Exiting from the engine")
    _set_running(False)


def _engine_step():
    _m_eCurrentScene.step_scene()


def _engine_draw():
    global _m_eCurrentScene, _m_rQueue, _m_rPrevRect
    _m_eCurrentScene.draw_scene()
    currentRect: Optional[pygame.Rect] = None
    while _m_rQueue:
        cObject: RenderObject = _m_rQueue.pop(0)
        try:
            newRect = _ENGINE_DRAW_FUNCTIONS[cObject.rType](cObject)
            if _m_eIsDebug:
                gx.rectangle(_m_rWindow, newRect, C_GREEN)
            if cObject.shouldAffect:
                currentRect = _engine_combine_rect(currentRect, newRect)
        except KeyError:
            _raise_engine_error(f"Invalid render type: {cObject.rType}")
    drawRect = None
    if currentRect:
        drawRect = _engine_combine_rect(currentRect, _m_rPrevRect)
    elif _m_rPrevRect:
        drawRect = _m_rPrevRect
    if drawRect:
        pygame.display.update(drawRect)
        # print(f"Updated {drawRect}")
    _m_rPrevRect = currentRect


def _engine_gather_input():
    for event in pygame.event.get():
        functs = []
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
            global _m_eMouseCallback
            functs = _m_eMouseCallback
        elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            global _m_eKeyCallback
            functs = _m_eKeyCallback
        elif event.type == pygame.QUIT:
            _engine_quit()
            return
        for funct in functs:
            funct(event)


def _create_window():
    global _m_rWindow
    _m_rWindow = pygame.display.set_mode(_m_rResolution)


def _engine_draw_rect(obj: RenderObject) -> pygame.Rect:
    """
    Performs drawing operations for all rect-like render objects
    :param obj: RenderObject to draw
    :return: The bounding rectangle of the object
    """
    rect = pygame.Rect(obj.x, obj.y, obj.w, obj.h)
    if obj.col:
        gx.box(_m_rWindow, rect, obj.col)
    if obj.oWidth and obj.oCol:
        gx.rectangle(_m_rWindow, rect, obj.oCol)
    return rect


def _engine_draw_ellipse(obj: RenderObject) -> pygame.Rect:
    """
    Performs drawing operations for all rect-like render objects
    :param obj: RenderObject to draw
    :return: The bounding rectangle of the object
    """
    rect = pygame.Rect(obj.x - obj.w - obj.oWidth, obj.y - obj.h - obj.oWidth,
                       (obj.w + obj.oWidth) * 2, (obj.h + obj.oWidth) * 2)
    gx.filled_ellipse(_m_rWindow, int(obj.x), int(obj.y), obj.w, obj.h, obj.col)
    tCol = obj.oCol if obj.oCol != C_BLACK else obj.col
    gx.aaellipse(_m_rWindow, int(obj.x), int(obj.y), obj.w, obj.h, tCol)
    return rect


def _engine_draw_default_texture(x: int, y: int) -> pygame.Rect:
    """
    Draws the default engine texture
    :param x: x position to draw to
    :param y: y position to draw to
    :return: the rect of the drawn texture
    """
    gx.box(_m_rWindow, (x, y, 50, 50), C_BLACK)
    gx.box(_m_rWindow, (x, y, 25, 25), (255, 16, 240))
    gx.box(_m_rWindow, (x + 25, y + 25, 25, 25), (255, 16, 240))
    return pygame.Rect(x, y, 50, 50)


def _engine_draw_texture(obj: RenderObject) -> pygame.Rect:
    """
    Performs all the drawing operations for textures
    :param obj: texture RenderObject
    :return: rectangle of the texture rendered
    """
    if obj.path not in _m_rTextureBank:
        return _engine_draw_default_texture(int(obj.x), int(obj.y))
    drawTexture = _m_rTextureBank[obj.path]
    cacheString = f"{obj.path}w{obj.w}h{obj.h}"
    if (obj.w or obj.h) and cacheString in _m_rTextureBank:
        drawTexture = _m_rTextureBank[cacheString]
    elif obj.w or obj.h:
        drawTexture = pygame.transform.scale(_m_rTextureBank[obj.path], (obj.w, obj.h))
    _m_rWindow.blit(drawTexture, (obj.x, obj.y))
    return drawTexture.get_rect()


def _cleanup_textures():
    for texture in _m_rToCleanup:
        del _m_rTextureBank[texture]


def _add_render_object(obj: RenderObject):
    global _m_rQueue
    _m_rQueue.append(obj)


_ENGINE_DRAW_FUNCTIONS = {
    "rect": _engine_draw_rect,
    "ellipse": _engine_draw_ellipse,
    "texture": _engine_draw_texture
}


def _engine_key_handle(event: pygame.event.Event):
    pass


""" ---------- EXPOSED ENGINE FUNCTIONS --------------"""


def get_engine_time():
    """
    Gets the current engine time in miliseconds
    :return:
    """
    return time.perf_counter() * 1e3


def ticks_to_time(ticks: float) -> float:
    """
    Calculates the total time that the specified amount of ticks would take to step
    :param ticks: number of ticks to calculate
    :return: time in ms
    """
    return ticks * (1e3 / _m_eTickrate)


def time_to_ticks(_time: float) -> int:
    """
    Calculates the amount of full steps the engine would take in a given timeframe
    :param _time: time in miliseconds
    :return: complete steps
    """
    return math.floor(_time * (_m_eTickrate / 1e3))


def refresh_window(refresh: [tuple, str] = C_BLACK):
    global _m_rLastRefresh
    is_col = isinstance(refresh, tuple)
    render_type = "rect" if is_col else "texture"
    render_colour = refresh if is_col else None
    render_path = refresh if not is_col else None
    _add_render_object(RenderObject(0, 0, _m_rResolution[0], _m_rResolution[1], render_type,
                                    col=render_colour, path=render_path, shouldAffect=_m_rLastRefresh != refresh))
    _m_rLastRefresh = refresh


def draw_rect(x: float, y: float, w: int, h: int, colour: tuple = C_BLACK, outlineWidth: int = 1) -> None:
    """
    Draws an outline of a rectangle
    :param x: x coordinate of the top left corner
    :param y: y coordinate of the top left corner
    :param w: width of the rectangle
    :param h: height of the rectangle
    :param colour: colour of the outline (default black)
    :param outlineWidth: width of the rectangle outline (default 1)
    :return: None
    """
    _add_render_object(RenderObject(x, y, w, h, "rect", oCol=colour, oWidth=outlineWidth))


def fill_rect(x: float, y: float, w: int, h: int, colour: tuple,
              outlineWidth: int = 0, outlineColour: tuple = C_BLACK) -> None:
    """
    Draws a filled rectangle
    :param x: x coordinate of the top left corner
    :param y: y coordinate of the top left corner
    :param w: width of the rectangle
    :param h: height of the rectangle
    :param colour: colour of the fill
    :param outlineWidth: width of the outline (optional)
    :param outlineColour: colour of the outline (optional, default black)
    :return: None
    """
    _add_render_object(RenderObject(x, y, w, h, "rect", col=colour, oCol=outlineColour, oWidth=outlineWidth))


def draw_square(x: float, y: float, length: int, colour: tuple = C_BLACK, outlineWidth: int = 1) -> None:
    """
    Draws an outline of a square
    :param x: x coordinate of the top-left corner
    :param y: y coordinate of the top-left corner
    :param length: length of the sides of the square
    :param colour: colour of the outline (default black)
    :param outlineWidth: outline width of the square (default 1)
    :return:
    """
    draw_rect(x, y, length, length, colour, outlineWidth)


def fill_square(x: float, y: float, length: int, colour: tuple,
                outlineWidth: int = 0, outlineColour: tuple = C_BLACK) -> None:
    """
    Draws a filled square
    :param x: x coordinate of top-left corner
    :param y: y coordinate of top-left corner
    :param length: length of the sides of the square
    :param colour: fill colour
    :param outlineWidth: outline width (optional)
    :param outlineColour: outline colour (default black)
    :return: None
    """
    fill_rect(x, y, length, length, colour, outlineWidth, outlineColour)


def draw_ellipse(x: float, y: float, rX: int, rY: int, colour: tuple, outlineWidth: int = 1) -> None:
    _add_render_object(RenderObject(x, y, rX, rY, "ellipse", oCol=colour, oWidth=outlineWidth))


def fill_ellipse(x: float, y: float, rX: int, rY: int, colour: tuple,
                 outlineWidth: int = 1, outlineColour: tuple = C_BLACK) -> None:
    _add_render_object(RenderObject(x, y, rX, rY, "ellipse", col=colour, oWidth=outlineWidth, oCol=outlineColour))


def draw_circle(x: float, y: float, r: int, colour: tuple, outlineWidth: int = 1) -> None:
    draw_ellipse(x, y, r, r, colour, outlineWidth)


def fill_circle(x: float, y: float, r: int, colour: tuple,
                outlineWidth: int = 1, outlineColour: tuple = C_BLACK) -> None:
    fill_ellipse(x, y, r, r, colour, outlineWidth, outlineColour)


def draw_texture(x: float, y: float, textureID: str, width: int = None, height: int = None,
                 shouldCache: bool = True) -> None:
    _add_render_object(RenderObject(x, y, width, height, "texture", path=textureID, shouldCache=shouldCache))


def load_texture(path: str, texID: str, newwidth: int = 0, newheight: int = 0, isstatic=False) -> False:
    """
    Loads a texture at the given path
    :param path: Path to the image
    :param texID: ID used to reference the texture
    :param newwidth: new width of the image (must be used in conjunctuion with newheight
    :param newheight: new height of the image (must be used in conjunction with newidth)
    :param isstatic: An image is static if it will never change position / size
    :return: None
    """
    if not os.path.isfile(path):
        _m_eEngineLogger.warning(f"Could not find texture ID {texID} at {path}")
        return
    if texID in _m_rTextureBank:
        _m_eEngineLogger.warning(f"Texture ID {texID} is being overwritten with the image at {path}")
    _m_rTextureBank[texID] = pygame.image.load(path).convert()
    # rescale to new width
    tWidth = newwidth if newwidth else _m_rTextureBank[texID].get_width()
    tHeight = newheight if newheight else _m_rTextureBank[texID].get_height()
    _m_rTextureBank[texID] = pygame.transform.scale(_m_rTextureBank[texID], (tWidth, tHeight))


def mark_texture_for_cleanup(texID: str) -> None:
    if texID not in _m_rTextureBank:
        _m_eEngineLogger.warning(f"Attempting to mark {texID} for cleanup when it does not exist!")
        return
    global _m_rToCleanup
    _m_rToCleanup.append(texID)


def init():
    if not pygame.get_init():
        pygame.init()
    global _m_eClientLogger, _m_eEngineLogger
    logfile = f"logs/{EngineLog.Logger.get_date_time()}.log"
    _m_eClientLogger = EngineLog.Logger(logfile, "CLIENT")
    _m_eEngineLogger = EngineLog.Logger(logfile, "ENGINE")
    _m_eEngineLogger.info("Initialised engine!")
    add_key_callback(_engine_key_handle)
    _create_window()
    _set_init(True)


def _exit():
    pygame.quit()
    sys.exit(0)


def run(initialScene: Scene.Scene) -> None:
    """
    Actually runs the engine
    :param initialScene: the initial scene that the engine should run
    :return: None
    """
    _set_running(True)
    if not get_init():
        # TODO this does not work in debug as logger has not been initialised
        _raise_engine_error("Attempting to run engine when it is uninitialised. See documentation for more.")
        _exit()
    _m_eEngineLogger.info("Starting Engine...")
    set_scene(initialScene)
    pTime = 0
    lag = 0
    frames = 0
    phys_steps = 0
    ticks = 0
    global _m_eTimePerTick, _m_eFPS, _m_eTPS
    while get_running():
        cTime = get_engine_time()
        elapsedTime = cTime - pTime
        lag += elapsedTime
        _engine_gather_input()
        while lag >= _m_eTimePerTick:
            _engine_step()
            step_client_tickbase(1)
            ticks += 1
            if get_client_tickbase() % get_engine_tickrate() == 0:
                _m_eFPS = frames
                _m_eTPS = ticks
                print(f"Frames: {_m_eFPS}")
                print(f"Ticks: {_m_eTPS}")
                print(f"Physics steps: {phys_steps}")
                phys_steps = 0
                frames = 0
                ticks = 0
            lag -= _m_eTimePerTick
        _engine_draw()
        frames += 1
        pTime = cTime
    _exit()
