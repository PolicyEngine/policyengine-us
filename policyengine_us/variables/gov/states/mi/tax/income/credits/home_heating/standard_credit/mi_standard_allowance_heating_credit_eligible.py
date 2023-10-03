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
        # the poverty guidelines are determined by the number of exemptions
        # which is a function of the tax_unit_size which is used in tax_unit_fpg
        fpg = tax_unit("tax_unit_fpg", period)

        return mi_household_resources <= (fpg * p.household_resources.fpg_rate)
