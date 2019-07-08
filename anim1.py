#!/usr/bin/env python3

from PyDoom.Graphics import DoomLabel, DoomSprite

from PyDoom.MusDecoder import MusDecoder
from PyDoom.WadSprite import WadPicture
from PyDoom.WadFile import WadFile

import threading
import optparse
import logging
import pygame
import time
import sys
import os
import io


logger = logging.getLogger ("pydoom")


class Timer(threading.Thread):
    def __init__(self, delegate, closure):
        threading.Thread.__init__(self)
        self.delegate = delegate
        self.closure = closure
        self.stopped = threading.Event()

    def stop(self):
        self.stopped.set()

    def run(self):
        while not self.stopped.wait(0.1):
            self.delegate(self.closure)


def main():
    global zombieIndex, shotgunZombieIndex, impIndex
    
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

    thingName = "IMP"
    entities = tuple(
        filter(lambda t: t.definition.name == thingName,
               wad.wad_levels["E1M2"].things)
    )
    if len(entities) == 0:
        raise Exception('unable to find [{0}] sprite set'.format(thingName))

    imp = entities[0]
    
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

    impIndex = 0
    doomImpSprite = DoomSprite(imp.sprite[impIndex], wad.playpals[0])
    doomImpSprite.x = 300
    
    doomImpLabel = DoomLabel (doomImpSprite.name, size=20)
    doomImpLabel.x = 300
    doomImpLabel.y = 100
    
    allSprites = pygame.sprite.Group(doomZombieSprite,
                                     doomZombieLabel,
                                     doomShotgunZombieSprite,
                                     doomShotgunZombieLabel,
                                     doomImpSprite,
                                     doomImpLabel)
    
    zombieIndex += 1
    shotgunZombieIndex += 1
    impIndex += 1

    def timerCallback(args):
        global zombieIndex, shotgunZombieIndex, impIndex
        zombieIndex = (zombieIndex + 1) % len(zombie.sprite)
        shotgunZombieIndex = (shotgunZombieIndex + 1) % len(shotgunZombie.sprite)
        impIndex = (impIndex + 1) % len(imp.sprite)
    
    timer = Timer(timerCallback, None)
    timer.start()

    running = True
    while running:
        for event in pygame.event.get ():
            if event.type == pygame.QUIT:
                timer.stop()
                timer.join()
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

        doomImpSprite.sprite = imp.sprite[impIndex]
        doomImpLabel.text = doomImpSprite.name

        # time.sleep(0.1)
        
        
    pygame.quit()
    
    
if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()
