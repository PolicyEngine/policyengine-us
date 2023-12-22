from policyengine_us.model_api import *


class ca_fytc(Variable):
    value_type = float
    entity = TaxUnit
    label = "California Foster Youth Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.credits.foster_youth

        eligible = tax_unit("ca_fytc_eligible", period)

        earned_income = tax_unit("filer_adjusted_earnings", period)
        is_tax_unit_spouse = person("is_tax_unit_spouse", period)
        is_tax_unit_head = person("is_tax_unit_head",period)

        reduction_amount = max_(0, (earned_income - p.threshold) * p.reduction)

        return tax_unit.sum(min_(p.max_amount, earned_income - reduction_amount) * eligible * (is_tax_unit_head|is_tax_unit_spouse))