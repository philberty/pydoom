#!/usr/bin/env python3

from PyDoom.MusDecoder import MusDecoder
from PyDoom.WadSprite import WadPicture
from PyDoom.WadFile import WadFile

import optparse
import logging
import pygame
import time
import sys
import os
import io


logger = logging.getLogger ("pydoom")


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


def main():
    parser = optparse.OptionParser()
    options, args = parser.parse_args()

    if len(args) < 1:
        sys.exit("No specified input wad-file provided")

    input_wad_file = args[0]
    wad = WadFile.load(input_wad_file)

    # to avoid conflict there can be multiple wad elements
    # of the same name so they are stored in a list
    # level_music = wad['D_E1M1'][0]
    # decoded_music = MusDecoder.decode_mus_to_midi(level_music)

    # musicBytes = io.BytesIO(decoded_music)
    # pygame.mixer.music.load(musicBytes)
    # pygame.mixer.music.play()
    
    thingName = "FORMER_HUMAN"
    entities = tuple(
        filter(lambda t: t.definition.name == thingName,
               wad.wad_levels["E1M1"].things)
    )
    if len(entities) == 0:
        raise Exception('unable to find [{0}] sprite set'.format(thingName))

    zombie = entities[0]

    thingName = "FORMER_HUMAN_SERGEANT"
    entities = tuple(
        filter(lambda t: t.definition.name == thingName,
               wad.wad_levels["E1M1"].things)
    )
    if len(entities) == 0:
        raise Exception('unable to find [{0}] sprite set'.format(thingName))

    shotgunZombie = entities[0]
    
    pygame.init ()
    width = 640
    height = 480
    screen_dimensions = width, height
    screen = pygame.display.set_mode (screen_dimensions)

    # get a thing to draw
    zombieIndex = 0
    shotgunZombieIndex = 0

    background = pygame.Surface(screen.get_size())
    background.fill((255, 255, 255))
    screen.blit(background, (0, 0))
    
    doomZombieSprite = DoomSprite (zombie.sprite[zombieIndex],
                                   wad.playpals[0])
    doomZombieLabel = DoomLabel (doomZombieSprite.name, size=20)
    doomZombieLabel.y = 100

    doomShotgunZombieSprite = DoomSprite (shotgunZombie.sprite[shotgunZombieIndex],
                                          wad.playpals[0])
    doomShotgunZombieSprite.x = 150
    
    doomShotgunZombieLabel = DoomLabel (doomShotgunZombieSprite.name, size=20)
    doomShotgunZombieLabel.x = 150
    doomShotgunZombieLabel.y = 100
    
    allSprites = pygame.sprite.Group(doomZombieSprite,
                                     doomZombieLabel,
                                     doomShotgunZombieSprite,
                                     doomShotgunZombieLabel)
    zombieIndex += 1
    shotgunZombieIndex += 1
    
    running = True
    while running:
        for event in pygame.event.get ():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    zombieIndex += 1
                    if zombieIndex >= len(zombie.sprite):
                        zombieIndex = 0
                
                if event.key == pygame.K_LEFT:
                    zombieIndex -= 1
                    if zombieIndex == 0:
                        zombieIndex = len(zombie.sprite) - 1

                if event.key == pygame.K_a:
                    shotgunZombieIndex += 1
                    if shotgunZombieIndex >= len(shotgunZombie.sprite):
                        shotgunZombieIndex = 0
                
                if event.key == pygame.K_d:
                    shotgunZombieIndex -= 1
                    if shotgunZombieIndex == 0:
                        shotgunZombieIndex = len(shotgunZombie.sprite) - 1

        allSprites.clear(screen, background)
        allSprites.update()
        allSprites.draw(screen)
        pygame.display.flip ()
        
        doomZombieSprite.sprite = zombie.sprite[zombieIndex]
        doomZombieLabel.text = doomZombieSprite.name

        doomShotgunZombieSprite.sprite = shotgunZombie.sprite[shotgunZombieIndex]
        doomShotgunZombieLabel.text = doomShotgunZombieSprite.name

        # time.sleep(0.1)
        
        
    pygame.quit()
    
    
if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()
