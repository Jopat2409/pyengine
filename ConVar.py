_convars = {}


class ConVar:

   def __init__(self, _type: type, _name: str, initial_value):
      global _convars
      self._m_value: _type = initial_value
      self._m_type: type = _type
      _convars[_name] = self

   def SetValue(self, newval):
      if not isinstance(newval, self._m_type):
         try:
            self._m_value = self._m_type(newval)
         except TypeError:
            pass
         return
      self._m_value = newval

   def GetValue(self):
      return self._m_value


def get_startswith(name: str) -> list:
   return [(cvar, _convars[cvar].GetValue()) for cvar in _convars if cvar.startswith(name)]


def get_convar(name: str) -> ConVar:
   if name in _convars:
      return _convars[name]
