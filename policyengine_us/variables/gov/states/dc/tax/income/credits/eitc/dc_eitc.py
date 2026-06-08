from policyengine_us.model_api import *


class dc_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC EITC"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.04",  # (f)
        "https://code.dccouncil.gov/us/dc/council/laws/23-149",  # D.C. Law 23-149 ITIN expansion
    )
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        # D.C. Law 23-149 extends EITC eligibility to filers and qualifying
        # children with ITINs.
        person = tax_unit.members
        dc_qualifying_child = person("is_qualifying_child_dependent", period) & person(
            "has_tin", period
        )
        return where(
            tax_unit.sum(dc_qualifying_child) > 0,
            tax_unit("dc_eitc_with_qualifying_child", period),
            tax_unit("dc_eitc_without_qualifying_child", period),
        )
