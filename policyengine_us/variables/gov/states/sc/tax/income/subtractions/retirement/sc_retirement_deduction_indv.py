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
    defined_for = StateCode.SC

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sc.tax.income.subtractions.retirement
        age = person("age", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # line 1
        max_deduction_allowed = p.cap.calc(age)
        # line 2: the deduction claimed under 12-6-1171 (12-6-1170(C)(1)),
        # not gross military retirement pay.
        military_retirement_deduction = person("sc_military_deduction_indv", period)
        # line 3
        retirement_deduction_available = max_(
            max_deduction_allowed - military_retirement_deduction, 0
        )
        # line 4: South Carolina counts income from all federal, state and
        # local public employee retirement plans (12-6-1170(A)(2)). NOAA and
        # PHS retired pay gets no 12-6-1171 deduction, so it counts here.
        retirement_income = (
            add(person, period, p.sources)
            + person("military_retirement_pay", period)
            - person("armed_forces_retirement_pay", period)
        ) * head_or_spouse
        # line 5
        return min_(retirement_deduction_available, retirement_income)
