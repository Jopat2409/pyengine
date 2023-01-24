"""
The main engine instance used to run programs using pyengine :)
"""
import ctypes
import math
import sys
import time
import pygame
from typing import Optional

import EngineLog
import Scene
from Constants import *

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


_m_rWindow: Optional[pygame.Surface] = None
_m_rQueue: list = []
_m_rPrevRect: Optional[pygame.Rect] = None

_m_rTexrtureBank: dict = {}
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


_m_eEngineLogger: Optional[EngineLog.Logger] = None
_m_eClientLogger: Optional[EngineLog.Logger] = None

""" ------------------ ENGINE PRIVATE FUNCTIONS -----------------"""


def _raise_engine_error(message: str) -> None:
   """
   Raises an engine error correctly depending on wether the engine is built in debug or release mode
   :param message: error log to print
   :return: None
   """
   if get_engine_debugmode():
      raise Exception(message)
   else:
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


def _engine_combine_rect(rect1: Optional[pygame.Rect], rect2: pygame.Rect) -> pygame.Rect:
   """
   Unionizes two pygame rectangles
   :param rect1: first rectangle (if none rect2 is returned)
   :param rect2: second rectangle (must be present)
   :return: Union of the two rectangles (or rect 2 if rect 1 is null)
   """
   if not rect1:
      return rect2
   mLeft = min(rect1.left, rect2.left)
   mTop = min(rect1.top, rect2.top)
   return pygame.Rect(mLeft, mTop, max(rect1.right, rect2.right) - mLeft, max(rect1.bottom, rect2.bottom) - mTop)


def _engine_quit():
   _set_running(False)


def _engine_step():
   pass


def _engine_draw():
   global _m_eCurrentScene, _m_rQueue, _m_rPrevRect
   _m_eCurrentScene.draw_scene()

   currentRect: Optional[pygame.Rect] = None
   while _m_rQueue:
      cObject = _m_rQueue.pop()
      if currentRect:
         pygame.display.update(_engine_combine_rect(currentRect, _m_rPrevRect))
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


def init():
   if not pygame.get_init():
      pygame.init()
   _create_window()
   _set_init(True)


def run(initialScene: Scene.Scene) -> None:
   """
   Actually runs the engine
   :param initialScene: the initial scene that the engine should run
   :return: None
   """
   if not get_init():
      _raise_engine_error("Attempting to run engine when it is uninitialised. See documentation for more.")
   _set_running(True)
   set_scene(initialScene)
   pTime = 0
   lag = 0
   frames = 0
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
            frames = 0
            ticks = 0
         lag -= _m_eTimePerTick
      _engine_draw()
      frames += 1
      pTime = cTime
   pygame.quit()
   sys.exit(0)
