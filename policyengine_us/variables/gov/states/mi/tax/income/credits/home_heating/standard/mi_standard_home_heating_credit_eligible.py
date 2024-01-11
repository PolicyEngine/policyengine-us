from policyengine_us.model_api import *


class mi_standard_home_heating_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Michigan home heating standard credit"
    definition_period = YEAR
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.home_heating.standard

        mi_household_resources = tax_unit("mi_household_resources", period)
        # the poverty guidelines are determined by the number of exemptions
        # which is a function of the tax_unit_size which is used in tax_unit_fpg
        fpg = tax_unit("tax_unit_fpg", period)
        limit = fpg * p.fpg_rate
        return mi_household_resources <= limit
