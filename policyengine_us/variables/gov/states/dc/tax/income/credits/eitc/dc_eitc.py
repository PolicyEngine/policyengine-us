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

    # DC EITC architecture:
    #   - dc_base_eitc: the SSN-only credit under section 47-1806.04 (federal
    #     IRC section 32 incorporation). This is the base statutory entitlement.
    #   - dc_eitc (this variable): the Law 23-149 ITIN-inclusive credit. Law
    #     23-149 (Earned Income Tax Credit Expansion Clarification Amendment
    #     Act of 2020) extends the EITC to filers and children with ITINs, so
    #     dc_eitc >= dc_base_eitc for any household.
    # The difference dc_eitc - dc_base_eitc is the incremental Law 23-149
    # benefit.

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
