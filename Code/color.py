class Color:

    # Member variables

    # self._red : str
    # self._green : str
    # self._blue : str
    # self._opacity : float (0...1)

    def __init__(self, red : int = 0, green : int = 0, blue : int = 0, opacity : float = 1.0):

        if (red < 0 or red > 255):
            raise ValueError("Red value is not in range 0...255.")
        if (green < 0 or green > 255):
            raise ValueError("Green value is not in range 0...255.")
        if (blue < 0 or blue > 255):
            raise ValueError("Blue value is not in range 0...255.")
        if (opacity < 0 or opacity > 1):
            raise ValueError("Opacity value is not in range 0...1.")

        self._red = hex(red)[2:].zfill(2)
        self._green = hex(green)[2:].zfill(2)
        self._blue = hex(blue)[2:].zfill(2)

        self._opacity = opacity

    def __mod__(self, opacity_factor : float):
        if opacity_factor < 0.0 or opacity_factor > 1.0:
            raise ValueError("Opacity factor has to be between 0.0 and 1.0.")
        return Color(int(self._red, 16),int(self._green, 16),int(self._blue, 16),self._opacity * opacity_factor)

    def getColor(self) -> str:
        if self._opacity == 0:
            return "None"
        else:
            return "#" + self._red + self._green + self._blue

    def getOpacity(self) -> float:
        return self._opacity

Black = Color(0,0,0,1)
White = Color(255,255,255,1)

Gray = Color(190,190,190,1)
DarkGray = Color(196,196,196,1)
LightGray = Color(211,211,211,1)

Red = Color(255,0,0,1)

Lime = Color(0,255,0,1)
Green = Color(0,139,0,1)

Blue = Color(0,0,255,1)

Yellow = Color(255,255,0,1)
Cyan = Color(0,255,255,1)
Magenta = Color(255,0,255,1)

NoFill = Color(0,0,0,0)