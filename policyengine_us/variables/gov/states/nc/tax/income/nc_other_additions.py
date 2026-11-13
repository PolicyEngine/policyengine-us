from policyengine_us.model_api import *


class nc_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC
    documentation = (
        "North Carolina additions to federal adjusted gross income reported on "
        "Form D-400 Schedule S, Part A, Line 16 (Total additions), "
        "entered as a positive amount, excluding additions PolicyEngine calculates separately."
    )
    reference = "https://www.ncdor.gov/2025-d-401-individual-income-tax-instructions/open#page=18"
