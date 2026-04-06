from policyengine_us.model_api import *


class ga_tanf_earned_income_after_disregard(Variable):
    value_type = float
    entity = Person
    label = "Georgia TANF earned income after work expense disregard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://pamms.dhs.ga.gov/dfcs/tanf/1615/",
        "https://pamms.dhs.ga.gov/dfcs/tanf/1605/",
    )
    defined_for = StateCode.GA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ga.dfcs.tanf.income.deductions
        # PAMMS 1615: "$250 is subtracted from the earned income of
        # each employed individual"
        # PAMMS 1605 Step 8: Apply earned income deductions to
        # "each employed individual"
        gross_earned = person("tanf_gross_earned_income", period)
        return max_(gross_earned - p.work_expense, 0)
