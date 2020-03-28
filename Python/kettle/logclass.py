LOG_LEVEL_ERROR = 1;
LOG_LEVEL_WARN = 2;
LOG_LEVEL_INFO = 3;
LOG_LEVEL_DEBUG = 4;


class logclass:
    def __init__(self, maxlvl=10):
        self.maxlevel = maxlvl;

    def error(self,mess):
        if (self.maxlevel >= LOG_LEVEL_ERROR):
            print ("ERROR1: ", mess)
    def warning(self,mess):
        if (self.maxlevel >= LOG_LEVEL_WARN):
            print ("WARN1:  ", mess)
    def info(self,mess):
        if (self.maxlevel >= LOG_LEVEL_INFO):
            print ("INFO1:  ", mess)
    def debug(self,mess):
        if (self.maxlevel >= LOG_LEVEL_DEBUG):
            print ("        Debug1: ", mess)

class log:
    maxlevel = 10

    def error(mess):
        if (log.maxlevel >= LOG_LEVEL_ERROR):
            print ("ERROR: ", mess)
    def warning(mess):
        if (log.maxlevel >= LOG_LEVEL_WARN):
            print ("WARN:  ", mess)
    def info(mess):
        if (log.maxlevel >= LOG_LEVEL_INFO):
            print ("INFO:  ", mess)
    def debug(mess):
        if (log.maxlevel >= LOG_LEVEL_DEBUG):
            print ("        Debug: ", mess)

