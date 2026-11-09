from policyengine_us.model_api import *


class state_withholding_agi(Variable):
    value_type = float
    entity = Person
    label = "Federal AGI that state income tax withholding reaches"
    unit = USD
    documentation = (
        "Each person's federal adjusted gross income "
        "(adjusted_gross_income_person) less the Railroad Retirement Act "
        "benefits it includes (taxable_railroad_benefits). 45 U.S.C. 231m(a) "
        "bars any state tax on those annuities. The state withholding "
        "estimates (the *_withheld_income_tax variables) start from this "
        "amount, and they feed the federal deduction for state and local "
        "income taxes."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/45/231m#a"

    def formula(person, period, parameters):
        agi = person("adjusted_gross_income_person", period)
        railroad = person("taxable_railroad_benefits", period)
        return agi - railroad
