from policyengine_us.model_api import *


class dc_senior_disabled_property_tax_relief_income(Variable):
    """Reference-year household AGI, projected to the public SPMUnit output.

    From 2025 this covers every resident of the physical household except
    fair-market tenants under written leases. Its explicit Household input
    represents 2023 AGI for property tax year 2025. No current-income or
    historical-membership inference supplies missing facts.
    """

    value_type = float
    entity = SPMUnit
    label = "DC senior disabled property tax relief household income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-863",
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/ASD%20100%20Instructions.pdf#page=1",
    )
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        return add(spm_unit, period, ["adjusted_gross_income"])

    def formula_2025(spm_unit, period, parameters):
        return spm_unit.household(
            "dc_senior_disabled_property_tax_relief_household_prior_agi", period
        )
