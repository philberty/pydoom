import pygame


class DoomLabel(pygame.sprite.Sprite):
    
    def __init__(self, text, font="monospace", size=15, antialised=True):
        pygame.sprite.Sprite.__init__(self)
        self._font = pygame.font.SysFont(font, size)
        self._text = text
        self._color = (0,0,0)
        self._x = 0
        self._y = 0
        self._antialised = antialised

    @property
    def font(self):
        return self._font

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value

    @property
    def antialised(self):
        return self._antialised

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    def update(self):
        self.image = self.font.render(self.text, self.antialised, self.color)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y


class DoomSprite(pygame.sprite.Sprite):

    def __init__(self, sprite, playpal):
        pygame.sprite.Sprite.__init__(self)
        self._sprite = sprite
        self._playpal = playpal
        self._x = 0
        self._y = 0

    @property
    def name(self):
        return self.sprite.name

    @property
    def playpal(self):
        return self._playpal

    @playpal.setter
    def playpal(self, value):
        self._playpal = value

    @property
    def sprite(self):
        return self._sprite

    @sprite.setter
    def sprite(self, value):
        self._sprite = value

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    def update(self):
        rgbPixels = WadPicture.pixelsToRgbPixels (self.sprite.pixels,
                                                  self.playpal)
        
        self.image = pygame.Surface((self.sprite.width, self.sprite.height))
        for w in range(self.sprite.width):
            for h in range(self.sprite.height):
                self.image.set_at ((w, h), rgbPixels[h][w])
                
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
