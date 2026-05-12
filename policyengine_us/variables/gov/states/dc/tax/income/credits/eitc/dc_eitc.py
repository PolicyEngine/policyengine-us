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

    # TODO: split into two named branches to mirror DC's statutory architecture:
    #   - dc_base_eitc: SSN-required, per section 47-1806.04 federal IRC section 32 incorporation
    #   - dc_itin_eitc: ITIN-eligible, per D.C. Law 23-149 (Earned Income Tax Credit Expansion Clarification Amendment)
    # The unified has_tin path below is behaviorally correct but conceptually merges the two.

    def formula(tax_unit, period, parameters):
        # D.C. Law 23-149 extends the EITC to filers and children with ITINs,
        # overriding the federal IRC section 32 SSN-only identification rule.
        person = tax_unit.members
        dc_qualifying_child = person("is_qualifying_child_dependent", period) & person(
            "has_tin", period
        )
        return where(
            tax_unit.sum(dc_qualifying_child) > 0,
            tax_unit("dc_eitc_with_qualifying_child", period),
            tax_unit("dc_eitc_without_qualifying_child", period),
        )
