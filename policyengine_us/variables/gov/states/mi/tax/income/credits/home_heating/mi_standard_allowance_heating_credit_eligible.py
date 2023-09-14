### add FPG file path
from policyengine_us.model_api import *


class mi_standard_allowance_heating_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Michigan home heating credit standard allowance"
    definition_period = YEAR
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.home_heating_credit.alternate_credit

        mi_household_resources = tax_unit("mi_household_resources", period)
        n = tax_unit("exemptions", period)

        state_group = "CONTIGUOUS_US"
        p_fpg = parameters(period).gov.hhs.fpg
        p1 = p_fpg.first_person[state_group]
        pn = p_fpg.additional_person[state_group]
        fpg = p1 + pn * (n - 1)

        return mi_household_resources <= (fpg * p.household_resources.fpg_rate)
