from adafruit_simple_text_display import SimpleTextDisplay

class editor(object):
    def __init__(self, display, title, ):
        self.display = display

        self.screen = None

        screenColors = (
            SimpleTextDisplay.YELLOW,
        )

        for q in range(1, display.height_lines-1):
            screenColors += (SimpleTextDisplay.WHITE,)

        screenColors += (SimpleTextDisplay.GREEN,)

        self.screen = SimpleTextDisplay(
            display=display.display,
            font=display.font,
            text_scale=1,
            colors=screenColors
        )

        self.title = title

    @property
    def title(self):
        return self._title
    
    @title.setter
    def title(self, value):
        self._title = value
        self.screen[0].text = self.title