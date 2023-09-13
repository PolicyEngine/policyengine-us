from policyengine_us.model_api import *


class sc_retirement_deduction_survivors(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina retirement deduction for survivors"
    defined_for = StateCode.SC
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
        military_retirement_pay_survivors = person(
            "military_retirement_pay_survivors", period
        )
        # line 3
        retirement_deduction_available = max_(
            max_deduction_allowed - military_retirement_pay_survivors, 0
        )
        # line 4
        retirement_income_survivors = person("pension_survivors", period)
        if p.subtract_military:
            return tax_unit.sum(
                min_(
                    retirement_deduction_available, retirement_income_survivors
                )
            )
        return tax_unit.sum(
            min_(max_deduction_allowed, retirement_income_survivors)
        )
