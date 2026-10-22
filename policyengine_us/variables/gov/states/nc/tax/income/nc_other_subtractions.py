from policyengine_us.model_api import *


class nc_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC
    documentation = (
        "North Carolina deductions/subtractions from federal adjusted gross income "
        "reported on Form D-400 Schedule S, Part B, Line 41 (Total deductions), "
        "entered as a positive amount, excluding subtractions PolicyEngine calculates separately."
    )
    reference = "https://www.ncdor.gov/2025-d-401-individual-income-tax-instructions/open#page=18"
