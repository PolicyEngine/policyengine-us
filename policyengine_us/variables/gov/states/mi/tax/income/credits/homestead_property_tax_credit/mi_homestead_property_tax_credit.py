from policyengine_us.model_api import *


class mi_homestead_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan Homestead Property Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = "mi_homestead_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.homestead_property_tax_credit

        total_household_resources = tax_unit("mi_household_resources", period)
        homestead_allowable = tax_unit("mi_homestead_allowable", period)

        phase_out_rate = p.rate.phase_out.calc(total_household_resources)

        return phase_out_rate * homestead_allowable
