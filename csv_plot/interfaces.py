from enum import Enum
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field, constr, validator


class Color(str, Enum):
    Aqua = "aqua"
    Black = "black"
    Blue = "blue"
    Fuchsia = "fuchsia"
    Gray = "gray"
    Green = "green"
    Lime = "lime"
    Maroon = "maroon"
    Navy = "navy"
    Olive = "olive"
    Orange = "orange"
    Purple = "purple"
    Red = "red"
    Silver = "silver"
    Teal = "teal"
    White = "white"
    Yellow = "yellow"


COLOR_NAME_TO_HEXA = {
    # https://clrs.cc/
    Color.Aqua: "#7FDBFF",
    Color.Black: "#111111",
    Color.Blue: "#0074D9",
    Color.Fuchsia: "F012BE",
    Color.Gray: "#AAAAAA",
    Color.Green: "#2ECC40",
    Color.Lime: "#01FF70",
    Color.Maroon: "85144b",
    Color.Navy: "#001f3f",
    Color.Olive: "#3D9970",
    Color.Orange: "#FF851B",
    Color.Purple: "#B10DC9",
    Color.Red: "#FF4136",
    Color.Silver: "#DDDDDD",
    Color.Teal: "#39CCCC",
    Color.White: "#FFFFFF",
    Color.Yellow: "#FFDC00",
}


class Configuration(BaseModel):
    class General(BaseModel):
        variable: str
        label: Optional[str]
        unit: Optional[str]
        as_datetime: bool = Field(False, alias="asDateTime")
        date_time_formats: Optional[List[str]] = Field(None, alias="dateTimeFormats")

    class LayoutItem(BaseModel):
        position: constr(regex=r"^[0-9]+-[0-9]+$")  # type: ignore
        title: Optional[str]
        label: Optional[str]
        unit: Optional[str]

        # Computed
        x: int = 0
        y: int = 0

        @validator("x", always=True)
        def set_x(cls, _, values: Dict[str, Any]) -> int:
            x, _ = values["position"].split("-")
            return int(x)

        @validator("y", always=True)
        def set_y(cls, _, values: Dict[str, Any]) -> int:
            _, y = values["position"].split("-")
            return int(y)

    class Curve(BaseModel):
        variable: str
        position: constr(regex=r"^[0-9]+-[0-9]+$") = "1-1"  # type: ignore
        color: Color = Color.Yellow

        # Computed
        x: int = 0
        y: int = 0

        @validator("x", always=True)
        def set_x(cls, _, values: Dict[str, Any]) -> int:
            x, _ = values["position"].split("-")
            return int(x)

        @validator("y", always=True)
        def set_y(cls, _, values: Dict[str, Any]) -> int:
            _, y = values["position"].split("-")
            return int(y)

    general: General
    layout: Optional[List[LayoutItem]]
    curves: List[Curve]
    variables: Set[str] = set()

    @validator("variables", always=True)
    def set_variables(cls, value, values: Dict[str, Any]) -> Set[str]:
        if "curves" not in values:
            return value

        return {curve.variable for curve in values["curves"]}
