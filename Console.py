import pygame.event
import ConVar
import Engine

_m_is_console_shown: bool = False


def get_showing() -> bool:
   return _m_is_console_shown


def set_shown(shouldshow: bool) -> None:
   global _m_is_console_shown
   _m_is_console_shown = shouldshow
   if shouldshow:
      Engine.add_key_callback(handle_keystroke)
   else:
      Engine.remove_key_callback(handle_keystroke)


def render_console(x: float, y: float) -> None:
   if not get_showing():
      return
   import Engine
   Engine.fill_rect(x, y, 200, 50, (100, 100, 100), 1)


_m_current_search_string: str = ""


def handle_keystroke(event: pygame.event.Event) -> None:
   if not get_showing():
      return
   print("handling console")
   if event.type == pygame.KEYUP:
      global _m_current_search_string
      if event.key == pygame.K_BACKSPACE:
         print("Removing letter :3")
         _m_current_search_string = _m_current_search_string[:-1]
      elif event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKQUOTE:
         set_shown(False)
      elif event.unicode != "":
         _m_current_search_string += event.unicode

      print(f"Current string: {_m_current_search_string}")
      print(ConVar.get_startswith(_m_current_search_string))


def init():
   Engine._m_eEngineLogger.info("Initialised Console!")
   Engine.add_system("Console", )
