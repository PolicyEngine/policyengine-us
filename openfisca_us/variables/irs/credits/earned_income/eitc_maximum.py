from openfisca_us.model_api import *


class eitc_maximum(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum EITC"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/32#a"
    unit = USD

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        num_children = tax_unit.sum(person("is_child", period))
        eitc = parameters(period).irs.credits.eitc
        maximum = eitc.max.calc(num_children)
        phased_in_rate = eitc.phase_in_rate.calc(num_children)
        earned_income = tax_unit("filer_earned", period)
        phased_in_amount = earned_income * phased_in_rate
        return min_(maximum, phased_in_amount)
