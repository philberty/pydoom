class WadDirectory:

## Fields
    _name = None
    _offset = None
    _size = None
    _data = None

## Constructor

    def __init__(self, name, offset, size, data):
        self._name = name
        self._offset = offset
        self._size = size
        self._data = data

## Properties

    @property
    def name(self):
        return self._name

    @property
    def offset(self):
        return self._offset

    @property
    def size(self):
        return self._size

    @property
    def data(self):
        return self._data

    @property
    def ok(self):
        return self._data is not None and len(self._data) == self._size

    def __len__(self):
        return self.size
