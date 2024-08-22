from policyengine_us.model_api import *


class sc_retirement_deduction_survivors(Variable):
    value_type = float
    entity = Person
    label = "South Carolina retirement deduction for survivors"
    defined_for = StateCode.SC
    unit = USD
    reference = (
        "https://www.scstatehouse.gov/code/t12c006.php",  # SECTION 12-6-1170(A)(1)
        "https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=17",
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sc.tax.income.subtractions.retirement
        age = person("age", period)
        # line 1
        max_deduction_allowed = p.cap.calc(age)
        # line 2
        military_retirement_pay_survivors = person(
            "military_retirement_pay_survivors", period
        )
        # line 3
        retirement_deduction_available = max_(
            max_deduction_allowed - military_retirement_pay_survivors, 0
        )
        # line 4
        retirement_income_survivors = person("pension_survivors", period)
        # In 2021, South Carolina subtracts the survivors retirement deduction from the military retirement deduction
        # In 2022, it does not
        cap = (
            retirement_deduction_available
            if p.subtract_military
            else max_deduction_allowed
        )
        return min_(retirement_income_survivors, cap)
