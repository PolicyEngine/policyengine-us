from policyengine_us.model_api import *


class mt_interest_exemption_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible person for the Montana interest exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=25"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.exemptions.interest
        age_head = tax_unit("age_head", period)
        eligible_aged_head = age_head >= p.age
        age_spouse = tax_unit("age_spouse", period)
        eligible_aged_spouse = age_spouse >= p.age
        return eligible_aged_head | eligible_aged_spouse
