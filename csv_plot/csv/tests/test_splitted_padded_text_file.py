# from typing import List
# import pytest

# from ..splitted_padded_text_file import BlockAndItemFinder


# @pytest.fixture
# def blocks_len() -> List[int]:
#     blocks = [[3, 4, 5], [6], [7, 8, 9, 10], [11, 12]]

#     return [len(block) for block in blocks]


# def test_block_and_item_finder_index_offset_0(blocks_len):
#     block_and_item_finder = BlockAndItemFinder(blocks_len, 0)

#     assert (len(block_and_item_finder)) == 10

#     with pytest.raises(IndexError):
#         block_and_item_finder[-11]

#     assert block_and_item_finder[0] == block_and_item_finder[-10] == (0, 0)
#     assert block_and_item_finder[1] == block_and_item_finder[-9] == (0, 1)
#     assert block_and_item_finder[2] == block_and_item_finder[-8] == (0, 2)
#     assert block_and_item_finder[3] == block_and_item_finder[-7] == (1, 0)
#     assert block_and_item_finder[4] == block_and_item_finder[-6] == (2, 0)
#     assert block_and_item_finder[5] == block_and_item_finder[-5] == (2, 1)
#     assert block_and_item_finder[6] == block_and_item_finder[-4] == (2, 2)
#     assert block_and_item_finder[7] == block_and_item_finder[-3] == (2, 3)
#     assert block_and_item_finder[8] == block_and_item_finder[-2] == (3, 0)
#     assert block_and_item_finder[9] == block_and_item_finder[-1] == (3, 1)

#     with pytest.raises(IndexError):
#         block_and_item_finder[10]


# def test_block_and_item_finder_index_offset_1(blocks_len):
#     block_and_item_finder = BlockAndItemFinder(blocks_len, 1)

#     assert (len(block_and_item_finder)) == 9

#     with pytest.raises(IndexError):
#         block_and_item_finder[-10]

#     assert block_and_item_finder[0] == block_and_item_finder[-9] == (0, 1)
#     assert block_and_item_finder[1] == block_and_item_finder[-8] == (0, 2)
#     assert block_and_item_finder[2] == block_and_item_finder[-7] == (1, 0)
#     assert block_and_item_finder[3] == block_and_item_finder[-6] == (2, 0)
#     assert block_and_item_finder[4] == block_and_item_finder[-5] == (2, 1)
#     assert block_and_item_finder[5] == block_and_item_finder[-4] == (2, 2)
#     assert block_and_item_finder[6] == block_and_item_finder[-3] == (2, 3)
#     assert block_and_item_finder[7] == block_and_item_finder[-2] == (3, 0)
#     assert block_and_item_finder[8] == block_and_item_finder[-1] == (3, 1)

#     with pytest.raises(IndexError):
#         block_and_item_finder[9]


# def test_block_and_item_finder_slice_offset_0(blocks_len):
#     block_and_item_finder = BlockAndItemFinder(blocks_len, 0)

#     assert block_and_item_finder[0:0] == [None, None, None, None]
#     assert block_and_item_finder[:1] == [slice(1), None, None, None]
#     assert block_and_item_finder[:2] == [slice(2), None, None, None]
#     assert block_and_item_finder[:3] == [slice(None), None, None, None]
#     assert block_and_item_finder[:4] == [slice(None), slice(None), None, None]
#     assert block_and_item_finder[:5] == [slice(None), slice(None), slice(1), None]
#     assert block_and_item_finder[:6] == [slice(None), slice(None), slice(2), None]
#     assert block_and_item_finder[:7] == [slice(None), slice(None), slice(3), None]
#     assert block_and_item_finder[:8] == [slice(None), slice(None), slice(None), None]

#     assert block_and_item_finder[:9] == [
#         slice(None),
#         slice(None),
#         slice(None),
#         slice(1),
#     ]

#     assert (
#         block_and_item_finder[:10]
#         == block_and_item_finder[:11]
#         == block_and_item_finder[:]
#         == [slice(None), slice(None), slice(None), slice(None)]
#     )

#     assert block_and_item_finder[3:4] == [None, slice(None), None, None]
#     assert block_and_item_finder[1:6] == [slice(1, None), slice(None), slice(2), None]

#     assert block_and_item_finder[:] == [
#         slice(None),
#         slice(None),
#         slice(None),
#         slice(None),
#     ]

#     assert block_and_item_finder[-3:] == [None, None, slice(3, None), slice(None)]


# def test_block_and_item_finder_slice_offset_1(blocks_len):
#     block_and_item_finder = BlockAndItemFinder(blocks_len, 1)

#     assert block_and_item_finder[0:0] == [None, None, None, None]
#     assert block_and_item_finder[:1] == [slice(1, 2), None, None, None]
#     # TODO: Should be `slice(1, None)` instead of `slice(1, 3)`
#     assert block_and_item_finder[:2] == [slice(1, 3), None, None, None]
#     assert block_and_item_finder[:3] == [slice(1, None), slice(None), None, None]
#     assert block_and_item_finder[:4] == [slice(1, None), slice(None), slice(1), None]
#     assert block_and_item_finder[:5] == [slice(1, None), slice(None), slice(2), None]
#     assert block_and_item_finder[:6] == [slice(1, None), slice(None), slice(3), None]
#     assert block_and_item_finder[:7] == [
#         slice(1, None),
#         slice(None),
#         slice(None),
#         None,
#     ]

#     assert (
#         block_and_item_finder[:9]
#         == block_and_item_finder[:10]
#         == block_and_item_finder[:]
#         == [
#             slice(1, None),
#             slice(None),
#             slice(None),
#             slice(None),
#         ]
#     )

#     assert block_and_item_finder[-3:] == [None, None, slice(3, None), slice(None)]
