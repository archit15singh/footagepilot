import unittest
from spliceforge.transcript import selection_ranges

class TranscriptSelection(unittest.TestCase):
    def test_rejected_take_and_padding(self):
        rows = [{'start':0,'end':1,'keep':False},{'start':2,'end':3,'keep':True},{'start':3.1,'end':4,'keep':True}]
        self.assertEqual(selection_ranges(rows, 5), [[1.92,4.08]])
    def test_empty_and_out_of_order_rejected(self):
        for rows in ([],[{'start':2,'end':1,'keep':True}],[{'start':0,'end':1,'keep':'false'}]):
            with self.assertRaises(ValueError):selection_ranges(rows,5)
