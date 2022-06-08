from armachat.ui_screen import Line as Line
from armachat.ui_screen import ui_screen as ui_screen
from armachat import config

from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

import displayio
import adafruit_imageload
import gc
import terminalio

class ui_splash(ui_screen):
    def __init__(self, ac_vars):
        ui_screen.__init__(self, ac_vars)

    def show(self):

        # Make the display context
        splash = displayio.Group()
        font_width, font_height = terminalio.FONT.get_bounding_box()

        if self.vars.display.display.height > 120:
            logo, pallet = \
                adafruit_imageload.load("armachat/Armachat Logo 120.bmp",
                                        bitmap=displayio.Bitmap,
                                        palette=displayio.Palette)

            font_scale = 2
            char_width = self.vars.display.display.width/(font_width * font_scale)
            text1 = "ARMACHAT " + config.model.upper()
            padding = " " * int((char_width - len(text1))/2)
            text_area1 = label.Label(
                terminalio.FONT, text=padding + text1 + padding + " ", scale=font_scale, background_tight=False, background_color=0x000000, color=0xFFFFFF
            )
            text_area1.x = 0
            text_area1.y = font_height

            text2 = "DOOMSDAY COMMUNICATOR"
            padding = " " * int((char_width - len(text2))/2)
            text_area2 = label.Label(
                terminalio.FONT, text=padding + text2 + padding + " ", scale=font_scale, background_tight=False, background_color=0x000000, color=0xFFFFFF
            )
            text_area2.x = 0
            # text_area2.y = font_height * 2 * font_scale
            text_area2.y = font_height * 3

            text3 = "Free RAM:" + str(gc.mem_free()) + " Loading ..."
            padding = " " * int((char_width - len(text3))/2)
            text_area3 = label.Label(
                terminalio.FONT, text=text3 + padding + " ", scale=font_scale, background_tight=False, background_color=0x0000FF, color=0xFFFFFF
            )
            text_area3.x = 0
            text_area3.y = self.vars.display.display.height - font_height

            tile_grid = displayio.TileGrid(logo,
                                    pixel_shader=pallet)

            tile_grid.x = int(self.vars.display.display.width/2 - logo.width/2)
            tile_grid.y = int(self.vars.display.display.height/2 - logo.height/2)
            
            splash.append(tile_grid)
            splash.append(text_area1)
            splash.append(text_area2)
            splash.append(text_area3)
        else:
            logo, pallet = \
                adafruit_imageload.load("armachat/Armachat Logo 80.bmp",
                                        bitmap=displayio.Bitmap,
                                        palette=displayio.Palette)

            font_scale = 1
            char_width = self.vars.display.display.width/(font_width * font_scale)
            text3 = "Free RAM:" + str(gc.mem_free()) + " Loading ..."
            padding = " " * int((char_width - len(text3))/2)
            text_area3 = label.Label(
                terminalio.FONT, text=text3 + padding + " ", scale=font_scale, background_tight=False, background_color=0x0000FF, color=0xFFFFFF
            )
            text_area3.x = 0
            text_area3.y = self.vars.display.display.height - int(font_height/2)

            tile_grid = displayio.TileGrid(logo,
                                    pixel_shader=pallet)

            tile_grid.x = int(self.vars.display.display.width/2 - logo.width/2)
            tile_grid.y = int(self.vars.display.display.height/2 - logo.height/2)
            
            splash.append(tile_grid)
            splash.append(text_area3)



        self.vars.display.display.show(splash)

        return None
