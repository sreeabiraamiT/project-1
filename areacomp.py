from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

area_avg = {
    "thanjavur": 248,
    "trichy": 271,
    "chennai": 310,
    "madurai": 265,
    "coimbatore": 289,
    "salem": 254,
    "tirunelveli": 242,
    "erode": 258
}

class CompareResponse(BaseModel):
    your_units: float
    area_average: float
    difference: float
    percent_difference: float


@router.get("/compare", response_model=CompareResponse)
def compare(area: str, units: float):

    avg = area_avg.get(area.strip().lower(), 270)  # default value

    difference = units - avg

    percent = round((difference / avg) * 100, 2)

    return CompareResponse(
        your_units=units,
        area_average=avg,
        difference=difference,
        percent_difference=percent
    )
