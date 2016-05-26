from PyDoom.WadDirectory import WadDirectory

from unittest import TestCase


class TestWadDirectory(TestCase):

    def test_directory_is_not_ok_on_invalid_data(self):
        invalid_size_directory = WadDirectory("Invalid", 0, 500, "invalid size")
        assert(invalid_size_directory.ok is False)

    def test_directory_is_not_ok_on_empty_data(self):
        invalid_size_directory = WadDirectory("Invalid", 0, 500, "")
        assert(invalid_size_directory.ok is False)

    def test_directory_is_not_ok_on_null_data(self):
        invalid_empty_directory = WadDirectory("Invalid", 0, 500, None)
        assert(invalid_empty_directory.ok is False)

    def test_directory_is_ok(self):
        valid_directory = WadDirectory("Valid", 0, 5, "Hello")
        assert(valid_directory.ok is True)

    def test_directory_contains_data(self):
        data = "Hello"
        valid_directory = WadDirectory("Valid", 0, len(data), data)
        assert(valid_directory.data is data)
