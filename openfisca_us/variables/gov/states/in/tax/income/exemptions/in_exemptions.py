from openfisca_us.model_api import *


class in_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN exemptions"
    unit = USD
    definition_period = YEAR
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5"  # (a)(1)-(5)
    defined_for = StateCode.IN

    formula = sum_of_variables(
        [
            "in_base_exemptions",
            "in_additional_exemptions",
            "in_aged_blind_exemptions",
            "in_aged_low_agi_exemptions",
        ]
    )
