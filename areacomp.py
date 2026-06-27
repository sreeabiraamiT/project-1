from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

area_avg = {
    "Chennai North": 420,
    "Chennai South": 390,
    "Coimbatore": 340,
    "Madurai": 310,
    "Thanjavur": 250,
    "Trichy": 280,
    "Salem": 295,
    "Tirunelveli": 270,
    "Vellore": 285,
    "Erode": 300

}

class CompareResponse(BaseModel):
    your_units: float
    area_average: float
    difference: float
    percent_difference: float


@router.get("/compare", response_model=CompareResponse)
def compare(area: str, units: float):

    avg = area_avg.get(area.strip().lower(), 270)  # default value

    difference = abs(units - avg)

    percent = round((difference / avg) * 100, 2)

    return CompareResponse(
        your_units=units,
        area_average=avg,
        difference=difference,
        percent_difference=percent
    )
