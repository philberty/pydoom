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

logger = logging.getLogger("pydoom")


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
    shotgunZombie.sprite[0].save_png("test_zombie.jpeg", wad.playpals[0])

    thingName = "IMP"
    entities = tuple(
        filter(lambda t: t.definition.name == thingName,
               wad.wad_levels["E1M2"].things)
    )
    if len(entities) == 0:
        raise Exception('unable to find [{0}] sprite set'.format(thingName))

    imp = entities[0]

    pygame.init()
    width = 640
    height = 480
    screen_dimensions = width, height
    screen = pygame.display.set_mode(screen_dimensions)

    # get a thing to draw
    zombieIndex = 0
    shotgunZombieIndex = 0

    background = pygame.Surface(screen.get_size())
    background.fill((255, 255, 255))
    screen.blit(background, (0, 0))

    doom_zombie_sprite = DoomSprite(zombie.sprite[zombieIndex],
                                    wad.playpals[0])
    doom_zombie_label = DoomLabel(doom_zombie_sprite.name, size=20)
    doom_zombie_label.y = 100

    doom_shotgun_zombie_sprite = DoomSprite(shotgunZombie.sprite[shotgunZombieIndex],
                                            wad.playpals[0])
    doom_shotgun_zombie_sprite.x = 150

    doom_shotgun_zombie_label = DoomLabel(doom_shotgun_zombie_sprite.name, size=20)
    doom_shotgun_zombie_label.x = 150
    doom_shotgun_zombie_label.y = 100

    impIndex = 0
    doom_imp_sprite = DoomSprite(imp.sprite[impIndex], wad.playpals[0])
    doom_imp_sprite.x = 300

    doom_imp_label = DoomLabel(doom_imp_sprite.name, size=20)
    doom_imp_label.x = 300
    doom_imp_label.y = 100

    all_sprites = pygame.sprite.Group(doom_zombie_sprite,
                                      doom_zombie_label,
                                      doom_shotgun_zombie_sprite,
                                      doom_shotgun_zombie_label,
                                      doom_imp_sprite,
                                      doom_imp_label)

    zombieIndex += 1
    shotgunZombieIndex += 1
    impIndex += 1

    def timer_callback(*args):
        global zombieIndex, shotgunZombieIndex, impIndex
        zombieIndex = (zombieIndex + 1) % len(zombie.sprite)
        shotgunZombieIndex = (shotgunZombieIndex + 1) % len(shotgunZombie.sprite)
        impIndex = (impIndex + 1) % len(imp.sprite)

    timer = Timer(timer_callback, None)
    timer.start()

    running = True
    while running:
        for event in pygame.event.get():
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

        all_sprites.clear(screen, background)
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()

        doom_zombie_sprite.sprite = zombie.sprite[zombieIndex]
        doom_zombie_label.text = doom_zombie_sprite.name

        doom_shotgun_zombie_sprite.sprite = shotgunZombie.sprite[shotgunZombieIndex]
        doom_shotgun_zombie_label.text = doom_shotgun_zombie_sprite.name

        doom_imp_sprite.sprite = imp.sprite[impIndex]
        doom_imp_label.text = doom_imp_sprite.name

        time.sleep(0.1)

    pygame.quit()


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()
