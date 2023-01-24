import os
import inspect
import datetime


class Logger:

   def __init__(self, logFile: str, entity: str):
      if not os.path.isfile(logFile):
         print(f"Creating file: {logFile}")
         with open(logFile, "w", encoding='utf-8'):
            pass
      self.m_logFile = open(logFile, "a", encoding='utf-8')
      self.m_logPath = logFile
      self.m_entity = entity

   def __del__(self):
      self.m_logFile.close()

   @staticmethod
   def get_current_time() -> str:
      return datetime.datetime.now().strftime('%M-%S-%f')[:-4]

   def _write_log_message(self, elevation: str, message: str, caller_module: str):
      self.m_logFile.write(f"{self.m_entity} : [{elevation} | {caller_module}][{Logger.get_current_time()}] : {message}")

   def info(self, message: str) -> None:
      caller_stackframe = inspect.stack()[1]
      caller_module = os.path.basename(caller_stackframe.filename)
      self._write_log_message("INFO", message, caller_module)

   def warning(self, message: str) -> None:
      caller_stackframe = inspect.stack()[1]
      caller_module = os.path.basename(caller_stackframe.filename)
      self._write_log_message("WARN", message, caller_module)

   def error(self, message: str) -> None:
      caller_stackframe = inspect.stack()[1]
      caller_module = os.path.basename(caller_stackframe.filename)
      self._write_log_message("ERROR", message, caller_module)
