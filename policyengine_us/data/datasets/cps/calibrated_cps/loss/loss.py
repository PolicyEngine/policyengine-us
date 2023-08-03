from .categories.populations import Populations
from survey_enhance.reweight import LossCategory
from policyengine_core.parameters import ParameterNode, uprate_parameters
from pathlib import Path


class Demographics(LossCategory):
    weight = 1
    subcategories = [Populations]


class Loss(LossCategory):
    subcategories = [
        Demographics,
    ]


calibration_parameters = ParameterNode(
    directory_path=Path(__file__).parent.parent / "calibration_parameters",
    name="calibration",
)

calibration_parameters = uprate_parameters(calibration_parameters)
