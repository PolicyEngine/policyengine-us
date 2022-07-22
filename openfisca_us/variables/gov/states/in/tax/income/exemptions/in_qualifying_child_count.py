from openfisca_us.model_api import *


class in_qualifying_child_count(Variable):
    value_type = int
    entity = TaxUnit
    label = "IN qualifying dependent child count"
    unit = "child"
    documentation = (
        "Number of qualifying children for the IN additional exemption."
    )
    definition_period = YEAR
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5"  # (5)(B)(i)
    defined_for = StateCode.IN

    formula = sum_of_variables(["in_is_qualifying_dependent_child"])
