class LogType():
    INFO = "Info"
    WARNING = "Warning"
    ERROR = "Error"

class log(object):
    def __init__(self, pyFile="", logFileName=None, usePrint=True, useFile=True):
        self.pyFile = pyFile
        self.logFileName = logFileName
        self.usePrint = usePrint
        self.useFile = useFile
        self._fsWriteMode = True

        if self.logFileName is None or len(self.logFileName) == 0:
            self.useFile = False

    # --- Public Methods ---
    def logMessage(self, method, msgTxt, status=LogType.INFO):
        if self.usePrint:
            self.printMessage(method, msgTxt, status)

        if self.useFile:
            self.writeMessage(method, msgTxt, status)

    def logValue(self, method, varName, varVal):
        msgTxt = varName + " -> " + str(varVal)
        self.logMessage(method, msgTxt)

        msgTxt = "type(" + varName + ") -> " + str(type(varVal))
        self.logMessage(method, msgTxt, LogType.INFO)

    # --- Internal Methods ---
    def printMessage(self, method, msgTxt, status=LogType.INFO):
        if not self.usePrint:
            return

        print(str(status) + "\t" + str(self.pyFile) + "\t" + str(method) +
              "\t" + str(msgTxt))

    def writeMessage(self, method, msgTxt, status=LogType.INFO):
        if not self.useFile or not self._fsWriteMode or self.logFileName is None:
            return

        fileText = str(status) + "\t" + str(self.pyFile) + "\t" + str(method) + \
            "\t" + str(msgTxt) + "\n"

        try:
            with open(self.logFileName, "a") as f:
                f.write(fileText)
        except OSError:
            print("messages.txt - Read Only File System")
            self._fsWriteMode = False
