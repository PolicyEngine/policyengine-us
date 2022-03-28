from openfisca_us.model_api import *


class eitc_maximum(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum EITC"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/32#a"
    unit = USD

    def formula(tax_unit, period, parameters):
        child_count = aggr(tax_unit, period, ["is_eitc_qualifying_child"])
        eitc = parameters(period).irs.credits.eitc
        maximum = eitc.max.calc(child_count)
        phased_in_rate = eitc.phase_in_rate.calc(child_count)
        earned_income = tax_unit("filer_earned", period)
        phased_in_amount = earned_income * phased_in_rate
        return min_(maximum, phased_in_amount)
