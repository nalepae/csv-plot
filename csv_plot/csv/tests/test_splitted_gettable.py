from typing import Iterable, List, Optional

import pytest

from ..splitted_gettable import SplittedGettable


class GettableList(list):
    def get(self, start: Optional[int], stop: Optional[int]) -> Iterable:
        for index in range(
            start if start is not None else 0,
            stop if stop is not None else len(self),
        ):
            yield self[index]


@pytest.fixture
def gettable_lists() -> List[GettableList]:
    return [
        GettableList(["a", "b", "c"]),
        GettableList(["d"]),
        GettableList(["e", "f", "g", "h"]),
        GettableList(["i", "j"]),
    ]


def test_splitted_iterable_index_offset_0(gettable_lists):
    splitted_iterable = SplittedGettable(gettable_lists, 0)

    assert (len(splitted_iterable)) == 10

    with pytest.raises(IndexError):
        splitted_iterable[-11]

    assert splitted_iterable[0] == splitted_iterable[-10] == "a"
    assert splitted_iterable[1] == splitted_iterable[-9] == "b"
    assert splitted_iterable[2] == splitted_iterable[-8] == "c"
    assert splitted_iterable[3] == splitted_iterable[-7] == "d"
    assert splitted_iterable[4] == splitted_iterable[-6] == "e"
    assert splitted_iterable[5] == splitted_iterable[-5] == "f"
    assert splitted_iterable[6] == splitted_iterable[-4] == "g"
    assert splitted_iterable[7] == splitted_iterable[-3] == "h"
    assert splitted_iterable[8] == splitted_iterable[-2] == "i"
    assert splitted_iterable[9] == splitted_iterable[-1] == "j"

    with pytest.raises(IndexError):
        splitted_iterable[10]


def test_splitted_iterable_slice_offset_0(gettable_lists):
    splitted_iterable = SplittedGettable(gettable_lists, 0)

    assert splitted_iterable[0:0] == []

    assert splitted_iterable[:1] == ["a"]
    assert splitted_iterable[:2] == ["a", "b"]
    assert splitted_iterable[:3] == ["a", "b", "c"]
    assert splitted_iterable[:4] == ["a", "b", "c", "d"]
    assert splitted_iterable[:5] == ["a", "b", "c", "d", "e"]
    assert splitted_iterable[:6] == ["a", "b", "c", "d", "e", "f"]
    assert splitted_iterable[:7] == ["a", "b", "c", "d", "e", "f", "g"]
    assert splitted_iterable[:8] == ["a", "b", "c", "d", "e", "f", "g", "h"]
    assert splitted_iterable[:9] == ["a", "b", "c", "d", "e", "f", "g", "h", "i"]

    assert (
        splitted_iterable[:10]
        == splitted_iterable[:11]
        == splitted_iterable[:]
        == ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
    )

    assert splitted_iterable[-3:] == ["h", "i", "j"]


def test_splitted_iterable_index_offset_1(gettable_lists):
    splitted_iterable = SplittedGettable(gettable_lists, 1)

    assert (len(splitted_iterable)) == 9

    with pytest.raises(IndexError):
        splitted_iterable[-10]

    assert splitted_iterable[0] == splitted_iterable[-9] == "b"
    assert splitted_iterable[1] == splitted_iterable[-8] == "c"
    assert splitted_iterable[2] == splitted_iterable[-7] == "d"
    assert splitted_iterable[3] == splitted_iterable[-6] == "e"
    assert splitted_iterable[4] == splitted_iterable[-5] == "f"
    assert splitted_iterable[5] == splitted_iterable[-4] == "g"
    assert splitted_iterable[6] == splitted_iterable[-3] == "h"
    assert splitted_iterable[7] == splitted_iterable[-2] == "i"
    assert splitted_iterable[8] == splitted_iterable[-1] == "j"

    with pytest.raises(IndexError):
        splitted_iterable[9]


def test_splitted_iterable_slice_offset_1(gettable_lists):
    splitted_iterable = SplittedGettable(gettable_lists, 1)

    assert splitted_iterable[0:0] == []

    assert splitted_iterable[:1] == ["b"]
    assert splitted_iterable[:2] == ["b", "c"]
    assert splitted_iterable[:3] == ["b", "c", "d"]
    assert splitted_iterable[:4] == ["b", "c", "d", "e"]
    assert splitted_iterable[:5] == ["b", "c", "d", "e", "f"]
    assert splitted_iterable[:6] == ["b", "c", "d", "e", "f", "g"]
    assert splitted_iterable[:7] == ["b", "c", "d", "e", "f", "g", "h"]
    assert splitted_iterable[:8] == ["b", "c", "d", "e", "f", "g", "h", "i"]

    assert (
        splitted_iterable[:9]
        == splitted_iterable[:10]
        == splitted_iterable[:]
        == ["b", "c", "d", "e", "f", "g", "h", "i", "j"]
    )

    assert splitted_iterable[-3:] == ["h", "i", "j"]
