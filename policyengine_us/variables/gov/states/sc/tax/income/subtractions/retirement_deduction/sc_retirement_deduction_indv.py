from policyengine_us.model_api import *


class sc_retirement_deduction_indv(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina retirement deduction for eligible individuals"
    defined_for = "sc_retirement_deduction_indv_eligible"
    unit = USD
    reference = (
        "https://www.scstatehouse.gov/code/t12c006.php",  # SECTION 12-6-1170(A)(1)
        "https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=17",
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.sc.tax.income.subtractions.retirement_deduction
        p_cap = p.max_amount
        person = tax_unit.members
        age = person("age", period)
        # line 1
        max_deduction_allowed = where(
            age >= p.age_threshold,
            p_cap.older,
            p_cap.younger,
        )
        # line 2
        military_retirement_pay = person("sc_military_deduction_indv", period)
        # line 3
        retirement_deduction_available = max_(
            max_deduction_allowed - military_retirement_pay, 0
        )
        # line 4
        retirement_income = person("taxable_pension_income", period)
        # line 5
        return min_(retirement_deduction_available, retirement_income)
