from policyengine_us.model_api import *


class id_retirement_benefits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho retirement benefits"
    unit = USD
    documentation = "https://tax.idaho.gov/wp-content/uploads/forms/EFO00088/EFO00088_12-30-2022.pdf#page=1"
    definition_period = YEAR
    defined_for = "id_retirement_benefits_eligible"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.id.tax.income.deductions.retirement_benefits
        filing_status = tax_unit("filing_status", period)
        
        # Base retirement benefits deduction amount
        base_amt = p.amount[filing_status]
        # Social Security benefits received amount
        ss_amt = add(tax_unit, period, ["social_security_retirement"])
        # Base amount minus social Security benefits received amount
        ded_amt = max_(base_amt - ss_amt, 0)
        # Qualified retirement benefits included in federal income
        fi_amt = tax_unit.sum(person("taxable_pension_income", period) + person("military_retirement_pay", period))
        # The smaller one
        return min_(ded_amt, fi_amt)
