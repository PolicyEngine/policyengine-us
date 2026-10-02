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
        # IRC 152(c)(3)(B) waives the age test for a permanently and totally
        # disabled dependent, as both branch variables do.
        is_disabled_dependent = person("is_tax_unit_dependent", period) & person(
            "is_permanently_and_totally_disabled", period
        )
        dc_qualifying_child = (
            person("is_qualifying_child_dependent", period) | is_disabled_dependent
        ) & person("has_tin", period)
        return where(
            tax_unit.sum(dc_qualifying_child) > 0,
            tax_unit("dc_eitc_with_qualifying_child", period),
            tax_unit("dc_eitc_without_qualifying_child", period),
        )
