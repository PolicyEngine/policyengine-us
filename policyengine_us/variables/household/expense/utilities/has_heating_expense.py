from policyengine_us.model_api import *


class has_heating_expense(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Has heating costs"
    documentation = (
        "Whether the household incurs home heating costs separately from its rent or "
        "mortgage. By default this is true when the primary heating fuel's bill is "
        "positive and heat is not included in rent. A fuel bill cannot say what the "
        "fuel is used for, so a household whose heating cost is not the primary fuel's "
        "bill (for example, free gathered wood with a purchased propane or fuel oil "
        "backup heater) should set this fact directly. Electric and solar heat read "
        "pre_subsidy_electricity_expense, not the subsidy-netted electricity_expense, "
        "so electric-heat households must send the pre-subsidy bill."
    )
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-7/section-273.9#p-273.9(d)(6)(iii)(D)(1)"
    )

    def formula(spm_unit, period, parameters):
        # heating_expense is zero for NONE and UNSPECIFIED heating types, so
        # a positive bill already implies a known heating fuel.
        primary_fuel_bill = spm_unit("heating_expense", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        return (primary_fuel_bill > 0) & ~heat_in_rent
