from PyDoom.WadException import WadException


class WadElement(object):

    @staticmethod
    def element_size():
        raise WadException('element-size not implemented')
