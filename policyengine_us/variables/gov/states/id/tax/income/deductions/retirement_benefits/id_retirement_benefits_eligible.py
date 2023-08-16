from policyengine_us.model_api import *


class id_retirement_benefits_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho retirement benefits"
    unit = USD
    documentation = "https://tax.idaho.gov/wp-content/uploads/forms/EFO00088/EFO00088_12-30-2022.pdf#page=1"
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        p = parameters(period).gov.states.id.tax.income.deductions.retirement_benefits

        age_threshold = p.age_eligibility.main
        age_threshold_disabled = p.age_eligibility.disabled
        disabled_head = tax_unit("disabled_head", period)
        eligible = where(disabled_head == False, 
                        tax_unit("age_head", period) >= age_threshold, 
                        tax_unit("age_head", period) >= age_threshold_disabled)
        
        return eligible