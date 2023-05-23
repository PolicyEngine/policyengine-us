from .categories import Population, EmploymentIncome
from survey_enhance.reweight import LossCategory
from policyengine_core.parameters import ParameterNode, uprate_parameters
from pathlib import Path


class Demographics(LossCategory):
    weight = 1
    subcategories = [Population]

class Programs(LossCategory):
    weight = 1
    subcategories = [EmploymentIncome]

class Loss(LossCategory):
    subcategories = [
        Demographics,
        Programs,
    ]


calibration_parameters = ParameterNode(
    directory_path=Path(__file__).parent.parent / "calibration_parameters",
    name="calibration",
)

calibration_parameters = uprate_parameters(calibration_parameters)
