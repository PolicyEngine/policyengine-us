from policyengine_us.model_api import *


class id_retirement_benefits(Variable):
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
        filing_status = tax_unit("filing_status", period)
        
        # check if filer is eligible for the deduction
        age_threshold = p.age_eligibility
        age_threshold_disabled = p.age_eligibility_disabled
        disabled_head = tax_unit("disabled_head", period)
        eligible = where(disabled_head == False, 
                            tax_unit("age_head", period) >= age_threshold, 
                            tax_unit("age_head", period) >= age_threshold_disabled)

        # Base retirement benefits deduction amount
        base_amt = p.amount[filing_status]
        # Social Security benefits received amount
        ss_amt = person("social_security_retirement", period)
        # Base amount minus social Security benefits received amount
        ded_amt = max_(base_amt - ss_amt, 0)
        # Qualified retirement benefits included in federal income
        fi_amt = person("taxable_pension_income", period) + person("military_retirement_pay", period)
        # The smaller one
        retire_ded_amt = min_(ded_amt, fi_amt)

        return eligible * tax_unit.sum(retire_ded_amt)
