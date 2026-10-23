from policyengine_us.model_api import *


class sc_retirement_deduction_survivors(Variable):
    value_type = float
    entity = Person
    label = "South Carolina retirement deduction for survivors"
    defined_for = StateCode.SC
    unit = USD
    reference = (
        "https://www.scstatehouse.gov/code/t12c006.php",  # SECTION 12-6-1170(A)(1)
        "https://dor.sc.gov/sites/dor/files/forms/SC1040Instr_2021.pdf",
        "https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=17",
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sc.tax.income.subtractions.retirement
        age = person("age", period)
        # line 1
        max_deduction_allowed = p.cap.calc(age)
        # Line 2 uses the military deduction claimed on line p-6, rather
        # than taxable survivor benefits that were not deducted.
        military_retirement_deduction = person(
            "sc_military_deduction_survivors", period
        )
        # line 3
        retirement_deduction_available = max_(
            max_deduction_allowed - military_retirement_deduction, 0
        )
        # line 4: only the head's and spouse's survivor benefits are in the
        # filer's federal AGI; a dependent reports their own on their own
        # return.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        retirement_income_survivors = (
            person("pension_survivors", period) * head_or_spouse
        )
        # In 2021, South Carolina subtracts the survivors retirement deduction from the military retirement deduction
        # In 2022, it does not
        cap = (
            retirement_deduction_available
            if p.subtract_military
            else max_deduction_allowed
        )
        return min_(retirement_income_survivors, cap)
