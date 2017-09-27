from PyDoom.WadElement import WadElement
from PyDoom.WadSprite import WadSprite

import struct
import ctypes

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

class ThingDefinition:

    def __init__(self, name, sprite):
        self._name = name
        self._sprite = sprite

    @property
    def name(self):
        return self._name

    @property
    def sprite(self):
        return self._sprite
    

THING_MAP = {
    0xFFFF: ThingDefinition("UNKNOWN_1", None),
    0x0000: ThingDefinition("UNKNOWN_2", None),
    0x0001: ThingDefinition("PLAYER_1_START", "PLAY"),
    0x0002: ThingDefinition("PLAYER_2_START", "PLAY"),
    0x0003: ThingDefinition("PLAYER_3_START", "PLAY"),
    0x0004: ThingDefinition("PLAYER_4_START", "PLAY"),
    0x000B: ThingDefinition("DEATHMATCH_START_POSITION", None),
    0x000E: ThingDefinition("TELEPORT_LANDING", None),
    
    0x0BBC: ThingDefinition("FORMER_HUMAN", "POSS"),
    0x0054: ThingDefinition("WOLFENSTEIN_SS", "SSWV"),
    0x0009: ThingDefinition("FORMER_HUMAN_SERGEANT", "SPOS"),
    0x0041: ThingDefinition("HEAVY_WEAPON_DUDE", "CPOS"),
    0x0BB9: ThingDefinition("IMP", "TROO"),
    0x0BBA: ThingDefinition("DEMON", "SARG"),
    0x0B3A: ThingDefinition("SPECTRE", "SARG"),
    0x0BBE: ThingDefinition("LOST_SOUL", "SKUL"),
    0x0BBD: ThingDefinition("CACODEMON", "HEAD"),
    0x0045: ThingDefinition("HELL_KNIGHT", "BOS2"),
    0x0044: ThingDefinition("ARACHNOTRON", "BSPI"),
    0x0047: ThingDefinition("PAIN_ELEMENTAL", "PAIN"),
    0x0042: ThingDefinition("REVENANT", "SKEL"),
    0x0043: ThingDefinition("MANCUBUS", "FATT"),
    0x0040: ThingDefinition("ARCH_VILE", "VILE"),
    0x0007: ThingDefinition("SPIDER_MASTERMIND", "SPID"),
    0x0010: ThingDefinition("CYBER-DEMON", "CYBR"),
    0x0058: ThingDefinition("BOSS_BRAIN", "BBRN"),
    0x0059: ThingDefinition("BOSS_SHOOTER", None),
    0x0057: ThingDefinition("SPAWN_SPOT", None),

    0x07D5: ThingDefinition("CHAINSAW", "CSAW"),
    0x07D1: ThingDefinition("SHOTGUN", "SHOT"),
    0x0052: ThingDefinition("DOUBLE_BARRELED_SHOTGUN", "SHN2"),
    0x07D2: ThingDefinition("CHAINGUN", "MGUN"),
    0x07D3: ThingDefinition("ROCKET_LAUNCHER", "LAUN"),
    0x07D4: ThingDefinition("PLASMA_GUN", "PLAS"),
    0x07D6: ThingDefinition("BFG_9000", "BFUG"),
    0x07D7: ThingDefinition("AMMO_CLIP", "CLIP"),
    0x07D8: ThingDefinition("SHELLS", "SHEL"),
    0x07DA: ThingDefinition("ROCKET", "ROCK"),
    0x07FF: ThingDefinition("CELL_CHARGE", "CELL"),
    0x0800: ThingDefinition("BOX_O_AMMO", "AMMO"),
    0x0801: ThingDefinition("BOX_O_SHELLS", "SBOX"),
    0x07FE: ThingDefinition("BOX_O_ROCKETS", "BROK"),
    0x0011: ThingDefinition("CELL_CHARGE_PACK", "CELP"),
    0x0008: ThingDefinition("BACKPACK", "BPAK"),

    0x07DB: ThingDefinition("STIMPACK", "STIM"),
    0x07DC: ThingDefinition("MEDIPACK", "MEDI"),
    0x07DE: ThingDefinition("POTION_1", "BON1"),
    0x07DF: ThingDefinition("POTION_2", "BON2"),
    0x07E2: ThingDefinition("GREEN_ARMOR", "ARM1"),
    0x07E3: ThingDefinition("BLUE_ARMOR", "ARM2"),
    0x0053: ThingDefinition("MEGASPHERE", "MEGA"),
    0x07DD: ThingDefinition("SOULSPHERE", "SOUL"),
    0x07E6: ThingDefinition("INVULNERABILITY", "PINV"),
    0x07E7: ThingDefinition("BESERKER", "PSTR"),
    0x07E8: ThingDefinition("INVISIBILITY", "PINS"),
    0x07E9: ThingDefinition("RAD_SUIT", "SUIT"),
    0x07EA: ThingDefinition("COMPUTER_MAP", "PMAP"),
    0x07FD: ThingDefinition("AMP_GOGGLES", "PVIS"),

    0x0005: ThingDefinition("BLUE_KEY", "BKEY"),
    0x0028: ThingDefinition("BLUE_SKULL_KEY", "BSKU"),
    0x000D: ThingDefinition("RED_KEY", "RKEY"),
    0x0026: ThingDefinition("RED_SKULL_KEY", "RSKU"),
    0x0006: ThingDefinition("YELLOW_KEY", "YKEY"),
    0x0027: ThingDefinition("YELLOW_SKULL_KEY", "YSKU"),

    0x07F3: ThingDefinition("BARREL", "BAR1"),
    0x0048: ThingDefinition("KEEN_BILLY", "KEEN"),

    0x0030: ThingDefinition("TALL_TECHNO_PILLAR", "ELEC"),
    0x001E: ThingDefinition("TALL_GREEN_PILLAR", "COL1"),
    0x0020: ThingDefinition("TALL_RED_PILLAR", "COL3"),
    0x001F: ThingDefinition("SHORT_GREEN_PILLAR", "COL2"),
    0x0024: ThingDefinition("SHORT_GREEN_PILLAR_BEATING_HEART", "COL5"),
    0x0021: ThingDefinition("SHORT_RED_PILLAR", "COL4"),
    0x0025: ThingDefinition("SHORT_RED_PILLAR_SKULL", "COL6"),
    0x002F: ThingDefinition("STALAGMITE", "SMIT"),
    0x002B: ThingDefinition("BURNT_TREE", "TRE1"),
    0x0036: ThingDefinition("LARGE_TREE", "TRE2"),

    0x07EC: ThingDefinition("FLOOR_LAMP", "COLU"),
    0x0055: ThingDefinition("TALL_TECHNO_FLOOR_LAMP", "TLMP"),
    0x0056: ThingDefinition("SHORT_TECHNO_FLOOR_LAMP", "TLP2"),
    0x0022: ThingDefinition("CANDLE", "CAND"),
    0x0023: ThingDefinition("CANDLELABRA", "CBRA"),
    0x002C: ThingDefinition("TALL_BLUE_FIRESTICK", "TBLU"),
    0x002D: ThingDefinition("TALL_GREEN_FIRESTICK", "TGRE"),
    0x002E: ThingDefinition("TALL_RED_FIRESTICK", "TRED"),
    0x0037: ThingDefinition("SHORT_BLUE_FIRESTICK", "SMBT"),
    0x0038: ThingDefinition("SHORT_GREEN_FIRESTICK", "SMGT"),
    0x0039: ThingDefinition("SHORT_RED_FIRESTICK", "SMRT"),
    0x0046: ThingDefinition("BURNING_BARREL", "FCAN"),

    0x0029: ThingDefinition("EVIL_EYE", "CEYE"),
    0x002A: ThingDefinition("FLOATING_SKULL", "FSKU"),
    
    0x0031: ThingDefinition("HANGING_VICTIM", "GOR1"),
    0x003F: ThingDefinition("HANGING_VICTIM_TWITCHING", "GOR1"),
    0x0032: ThingDefinition("HANGING_VICTIM_ARMS_OUT", "GOR2"),
    0x003B: ThingDefinition("HANGING_VICTIM_ARMS_OUT", "GOR2"),
    0x0034: ThingDefinition("HANGING_PAIR_LEGS", "GOR4"),
    0x003C: ThingDefinition("HANGING_PAIR_LEGS", "GOR4"),
    0x0033: ThingDefinition("HANGING_VICTIM_ONE_LEG", "GOR3"),
    0x003D: ThingDefinition("HANGING_VICTIM_ONE_LEG", "GOR3"),
    
    0x0035: ThingDefinition("HANGING_LEG", "GOR5"),
    0x003E: ThingDefinition("HANGING_LEG", "GOR5"),
    0x0049: ThingDefinition("HANGING_VICTIM_GUTS_REMOVED", "HDB1"),
    0x004A: ThingDefinition("HANGING_VICTIM_GUTS_BRAIN_REMOVED", "HDB2"),
    0x004B: ThingDefinition("HANGING_TORSODOWN_DOWN", "HDB3"),
    0x004C: ThingDefinition("HANGING_TORSODOWN_OPEN_SKULL", "HDB4"),
    0x004D: ThingDefinition("HANGING_TORSODOWN_UP", "HDB5"),
    0x004E: ThingDefinition("HANGING_TORSODOWN_BRAIN_REMOVED", "HDB6"),

    0x0019: ThingDefinition("IMPALED_HUMAN", "POL1"),
    0x001A: ThingDefinition("TWITCHING_IMPLAED_HUMAN", "POL6"),
    0x001B: ThingDefinition("SKULL_ON_POLE", "POL4"),
    0x001C: ThingDefinition("SKULLS_SHISH_KEBAB", "POL2"),
    0x001D: ThingDefinition("PILE_OF_SKULLS_AND_CANDLES", "POL3"),
    0x000A: ThingDefinition("BLOODY_MESS_EXPLODED_PLAYER", "PLAY"),
    0x000C: ThingDefinition("BLOODY_MESS_EXPLODED_PLAYER", "PLAY"),
    0x0018: ThingDefinition("POOL_OF_BLOOD_AND_FLESH", "POL5"),
    0x004F: ThingDefinition("POOL_OF_BLOOD1", "POB1"),
    0x0050: ThingDefinition("POOL_OF_BLOOD2", "POB2"),
    0x0051: ThingDefinition("POOL_OF_BRAINS", "BRS1"),
    0x000F: ThingDefinition("DEAD_PLAYER", "PLAY"),
    0x0012: ThingDefinition("DEAD_FORMER_HUMAN", "POSS"),
    0x0013: ThingDefinition("DEAD_FORMER_SERGENT", "SPOS"),
    0x0014: ThingDefinition("DEAD_IMP", "TROO"),
    0x0015: ThingDefinition("DEAD_DEMON", "SARG"),
    0x0016: ThingDefinition("DEAD_CACODEOMON", "HEAD"),
    0x0017: ThingDefinition("DEAD_LOST_SOUL_INVISIBLE", "SKUL")
}


class WadThing(WadElement):

    """
    http://doom.wikia.com/wiki/Thing - Specification
    """

    _x = None
    _y = None
    _angle = None
    _thing_type = None
    _flags = None

    def __init__(self, chunk, wad):
        super(WadThing, self).__init__()
        self._wad = wad
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

    @property
    def definition(self):
        return THING_MAP[self.thing_type]

    def safeDefinition(self, default=None):
        return THING_MAP.get(self.thing_type, default)

    def thingName(self, defaultName=None):
        definition = self.safeDefinition(default=None)
        if definition is None:
            return defaultName
        return definition.name

    @property
    def associatedLumps(self):
        spritePrefix = self.definition.sprite
        spriteKeys = filter(lambda i: i.startswith(spritePrefix), self._wad)
        return tuple(map(lambda i: self._wad[i][0], spriteKeys))

    @property
    def hasDefinition(self):
        return self.thing_type in THING_MAP
        
    @property
    def hasSprite(self):
        return self.hasDefinition and self.definition.sprite is not None

    @property
    def sprite(self):
        if not self.hasSprite:
            raise Exception("THING [{0}] does not have an associated sprite set" \
                            .format(self.definition.name))
        
        return WadSprite(self, self.associatedLumps)

    @staticmethod
    def element_size():
        return 10
