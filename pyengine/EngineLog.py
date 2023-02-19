import os
import inspect
import datetime


class Logger:

    def __init__(self, logFile: str, entity: str):
        if not os.path.isdir("logs"):
            os.mkdir("logs")
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
    def get_log_time() -> str:
        """
        Gets the current time in the format used by the logger
        :return: current time as a string
        """
        return datetime.datetime.now().strftime('%H:%M:%S')

    @staticmethod
    def get_date_time() -> str:
        """
        Gets the current time in a format usable for a logfile name
        :return: current time as string
        """
        return datetime.datetime.now().strftime('%d-%m-%Y-%H-%M-%S')

    def _write_log_message(self, elevation: str, message: str, caller_module: str) -> None:
        """
        Used internally to structure and format log messages
        :param elevation: level of log to log
        :param message: message to log
        :param caller_module: module the log is being called from
        :return: None
        """
        self.m_logFile.write(f"[{elevation}][{self.m_entity}:{caller_module}][{Logger.get_log_time()}] : {message}\n")

    def info(self, message: str) -> None:
        """
        Log an informational message
        :param message: message to log
        :return: None
        """
        caller_stackframe = inspect.stack()[1]
        caller_module = os.path.basename(caller_stackframe.filename)
        self._write_log_message("INFO", message, caller_module)

    def warning(self, message: str) -> None:
        """
        Log a warning message
        :param message: message to log
        :return: None
        """
        caller_stackframe = inspect.stack()[1]
        caller_module = os.path.basename(caller_stackframe.filename)
        self._write_log_message("WARN", message, caller_module)

    def error(self, message: str) -> None:
        """
        Log that an error has occured
        :param message: message to log
        :return: None
        """
        caller_stackframe = inspect.stack()[1]
        caller_module = os.path.basename(caller_stackframe.filename)
        self._write_log_message("ERROR", message, caller_module)
