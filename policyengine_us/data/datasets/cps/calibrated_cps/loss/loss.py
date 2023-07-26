from .categories import *
from .income_tax import *
from .populations import *
from survey_enhance.reweight import LossCategory
from policyengine_core.parameters import ParameterNode, uprate_parameters
from pathlib import Path


class Demographics(LossCategory):
    weight = 1
    subcategories = [
        Population,
        PopulationByAgeAndSex,
    ]

class Programs(LossCategory):
    weight = 4
    subcategories = [
        EmploymentIncome,
        AdjustedGrossIncome,
        TaxableInterestIncome,
        TaxExemptInterestIncome,
        NonQualifiedDividendIncome,
        QualifiedDividendIncome,
        SelfEmploymentIncome,
        CapitalGains,
        TaxablePensionIncome,
        PensionIncome,
        TaxableIncome,
        IncomeTax,
        SNAP,
        SocialSecurity,
        SSI,
        AGIByAGI,
        AGICountByAGI,
        IncomeTaxByAGI,
        IncomeTaxCountByAGI,
    ]


class Loss(LossCategory):
    subcategories = [
        Programs,
        Demographics,
    ]


calibration_parameters = ParameterNode(
    directory_path=Path(__file__).parent.parent / "calibration_parameters",
    name="calibration",
)

calibration_parameters = uprate_parameters(calibration_parameters)
