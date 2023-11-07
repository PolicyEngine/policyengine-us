from policyengine_us.model_api import *


class sc_retirement_deduction_indv(Variable):
    value_type = float
    entity = Person
    label = "South Carolina retirement deduction for eligible individuals"
    unit = USD
    reference = (
        "https://www.scstatehouse.gov/code/t12c006.php",  # SECTION 12-6-1170(A)(1)
        "https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=17",
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sc.tax.income.subtractions.retirement
        age = person("age", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # line 1
        max_deduction_allowed = p.cap.calc(age)
        # line 2
        military_retirement_pay = person("military_retirement_pay", period)
        # line 3
        retirement_deduction_available = max_(
            max_deduction_allowed - military_retirement_pay, 0
        )
        # line 4
        retirement_income = (
            person("taxable_pension_income", period) * head_or_spouse
        )
        # line 5
        return min_(retirement_deduction_available, retirement_income)
