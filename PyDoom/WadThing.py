from PyDoom.WadElement import WadElement

import struct

"""
Dec. Hex  V Spr  seq.     Thing is:

  -1 ffff   ---- -        (nothing)
   0 0000   ---- -        (nothing)
   1 0001   PLAY +        Player 1 start (Player 1 start needed on ALL
levels)
   2 0002   PLAY +        Player 2 start (Player starts 2-4 are needed in)
   3 0003   PLAY +        Player 3 start (cooperative mode multiplayer games)
   4 0004   PLAY +        Player 4 start
  11 000b   ---- -        Deathmatch start positions. Should have >= 4/level
  14 000e   ---- -        Teleport landing. Where players/monsters land when
  14                        they teleport to the SECTOR containing this thing

3004 0bbc   POSS +      # FORMER HUMAN: regular pistol-shooting zombieman
  84 0054 2 SSWV +      # WOLFENSTEIN SS: guest appearance by Wolf3D blue guy
   9 0009   SPOS +      # FORMER HUMAN SERGEANT: black armor, shotgunners
  65 0041 2 CPOS +      # HEAVY WEAPON DUDE: red armor, chaingunners
3001 0bb9   TROO +      # IMP: brown, hurl fireballs
3002 0bba   SARG +      # DEMON: pink, muscular bull-like chewers
  58 003a   SARG +      # SPECTRE: invisible version of the DEMON
3006 0bbe r SKUL +     ^# LOST SOUL: flying flaming skulls, they really bite
3005 0bbd r HEAD +     ^# CACODEMON: red one-eyed floating heads. Behold...
  69 0045 2 BOS2 +      # HELL KNIGHT: grey-not-pink BARON, weaker
3003 0bbb   BOSS +      # BARON OF HELL: cloven hooved minotaur boss
  68 0044 2 BSPI +      # ARACHNOTRON: baby SPIDER, shoots green plasma
  71 0047 2 PAIN +     ^# PAIN ELEMENTAL: shoots LOST SOULS, deserves its
name
  66 0042 2 SKEL +      # REVENANT: Fast skeletal dude shoots homing missles
  67 0043 2 FATT +      # MANCUBUS: Big, slow brown guy shoots barrage of
fire
  64 0040 2 VILE +      # ARCH-VILE: Super-fire attack, ressurects the dead!
   7 0007 r SPID +      # SPIDER MASTERMIND: giant walking brain boss
  16 0010 r CYBR +      # CYBER-DEMON: robo-boss, rocket launcher

  88 0058 2 BBRN +      # BOSS BRAIN: Horrifying visage of the ultimate demon
  89 0059 2 -    -        Boss Shooter: Shoots spinning skull-blocks
  87 0057 2 -    -        Spawn Spot: Where Todd McFarlane's guys appear

2005 07d5   CSAW a      $ Chainsaw
2001 07d1   SHOT a      $ Shotgun
  82 0052 2 SGN2 a      $ Double-barreled shotgun
2002 07d2   MGUN a      $ Chaingun, gatling gun, mini-gun, whatever
2003 07d3   LAUN a      $ Rocket launcher
2004 07d4 r PLAS a      $ Plasma gun
2006 07d6 r BFUG a      $ Bfg9000
2007 07d7   CLIP a      $ Ammo clip
2008 07d8   SHEL a      $ Shotgun shells
2010 07da   ROCK a      $ A rocket
2047 07ff r CELL a      $ Cell charge
2048 0800   AMMO a      $ Box of Ammo
2049 0801   SBOX a      $ Box of Shells
2046 07fe   BROK a      $ Box of Rockets
  17 0011 r CELP a      $ Cell charge pack
   8 0008   BPAK a      $ Backpack: doubles maximum ammo capacities

2011 07db   STIM a      $ Stimpak
2012 07dc   MEDI a      $ Medikit
2014 07de   BON1 abcdcb ! Health Potion +1% health
2015 07df   BON2 abcdcb ! Spirit Armor +1% armor
2018 07e2   ARM1 ab     $ Green armor 100%
2019 07e3   ARM2 ab     $ Blue armor 200%
  83 0053 2 MEGA abcd   ! Megasphere: 200% health, 200% armor
2013 07dd   SOUL abcdcb ! Soulsphere, Supercharge, +100% health
2022 07e6 r PINV abcd   ! Invulnerability
2023 07e7 r PSTR a      ! Berserk Strength and 100% health
2024 07e8   PINS abcd   ! Invisibility
2025 07e9   SUIT a     (!)Radiation suit - see notes on ! above
2026 07ea   PMAP abcdcb ! Computer map
2045 07fd   PVIS ab     ! Lite Amplification goggles

   5 0005   BKEY ab     $ Blue keycard
  40 0028 r BSKU ab     $ Blue skullkey
  13 000d   RKEY ab     $ Red keycard
  38 0026 r RSKU ab     $ Red skullkey
   6 0006   YKEY ab     $ Yellow keycard
  39 0027 r YSKU ab     $ Yellow skullkey

2035 07f3   BAR1 ab+    # Barrel; not an obstacle after blown up
                            (BEXP sprite)
  72 0048 2 KEEN a+     # A guest appearance by Billy

  48 0030   ELEC a      # Tall, techno pillar
  30 001e r COL1 a      # Tall green pillar
  32 0020 r COL3 a      # Tall red pillar
  31 001f r COL2 a      # Short green pillar
  36 0024 r COL5 ab     # Short green pillar with beating heart
  33 0021 r COL4 a      # Short red pillar
  37 0025 r COL6 a      # Short red pillar with skull
  47 002f r SMIT a      # Stalagmite: small brown pointy stump
  43 002b r TRE1 a      # Burnt tree: gray tree
  54 0036 r TRE2 a      # Large brown tree

2028 07ec   COLU a      # Floor lamp
  85 0055 2 TLMP abcd   # Tall techno floor lamp
  86 0056 2 TLP2 abcd   # Short techno floor lamp
  34 0022   CAND a        Candle
  35 0023   CBRA a      # Candelabra
  44 002c r TBLU abcd   # Tall blue firestick
  45 002d r TGRE abcd   # Tall green firestick
  46 002e   TRED abcd   # Tall red firestick
  55 0037 r SMBT abcd   # Short blue firestick
  56 0038 r SMGT abcd   # Short green firestick
  57 0039 r SMRT abcd   # Short red firestick
  70 0046 2 FCAN abc    # Burning barrel

  41 0029 r CEYE abcb   # Evil Eye: floating eye in symbol, over candle
  42 002a r FSKU abc    # Floating Skull: flaming skull-rock

  49 0031 r GOR1 abcb  ^# Hanging victim, twitching
  63 003f r GOR1 abcb  ^  Hanging victim, twitching
  50 0032 r GOR2 a     ^# Hanging victim, arms out
  59 003b r GOR2 a     ^  Hanging victim, arms out
  52 0034 r GOR4 a     ^# Hanging pair of legs
  60 003c r GOR4 a     ^  Hanging pair of legs
  51 0033 r GOR3 a     ^# Hanging victim, 1-legged
  61 003d r GOR3 a     ^  Hanging victim, 1-legged
  53 0035 r GOR5 a     ^# Hanging leg
  62 003e r GOR5 a     ^  Hanging leg
  73 0049 2 HDB1 a     ^# Hanging victim, guts removed
  74 004a 2 HDB2 a     ^# Hanging victim, guts and brain removed
  75 004b 2 HDB3 a     ^# Hanging torso, looking down
  76 004c 2 HDB4 a     ^# Hanging torso, open skull
  77 004d 2 HDB5 a     ^# Hanging torso, looking up
  78 004e 2 HDB6 a     ^# Hanging torso, brain removed

  25 0019 r POL1 a      # Impaled human
  26 001a r POL6 ab     # Twitching impaled human
  27 001b r POL4 a      # Skull on a pole
  28 001c r POL2 a      # 5 skulls shish kebob
  29 001d r POL3 ab     # Pile of skulls and candles
  10 000a   PLAY w        Bloody mess (an exploded player)
  12 000c   PLAY w        Bloody mess, this thing is exactly the same as 10
  24 0018   POL5 a        Pool of blood and flesh
  79 004f 2 POB1 a        Pool of blood
  80 0050 2 POB2 a        Pool of blood
  81 0051 2 BRS1 a        Pool of brains
  15 000f   PLAY n        Dead player
  18 0012   POSS l        Dead former human
  19 0013   SPOS l        Dead former sergeant
  20 0014   TROO m        Dead imp
  21 0015   SARG n        Dead demon
  22 0016 r HEAD l        Dead cacodemon
  23 0017 r SKUL k        Dead lost soul, invisible
                              (they blow up when killed)
"""

class WadThing(WadElement):

    """
    http://doom.wikia.com/wiki/Thing - Specification
    """

    _x = None
    _y = None
    _angle = None
    _thing_type = None
    _flags = None

    def __init__(self, chunk):
        super(WadThing, self).__init__()
        self._x, \
            self._y, \
            self._angle, \
            self._thing_type,\
            self._flags = struct.unpack("<hhhhh", chunk)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def angle(self):
        return self._angle

    @property
    def thing_type(self):
        return self._thing_type

    @property
    def flags(self):
        return self._flags

    @staticmethod
    def element_size():
        return 10
