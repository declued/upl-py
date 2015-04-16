import unittest

class UPLTestCase(unittest.TestCase):
    def matchValues(self, full_value, partial_value):
        self.assertEqual(type(full_value), type(partial_value))

        if isinstance(full_value, dict):
            self.matchDicts(full_value, partial_value)
        elif isinstance(full_value, list) or isinstance(partial_value, tuple):
            self.matchLists(full_value, partial_value)
        else:
            self.assertEqual(full_value, partial_value)

    def matchDicts(self, full_dict, partial_dict):
        for k, v in partial_dict.items():
            self.matchValues(full_dict.get(k), v)

    def matchLists(self, full_list, partial_list):
        self.assertEqual(len(partial_list), len(full_list))
        for v1, v2 in zip(full_list, partial_list):
            self.matchValues(v1, v2)

