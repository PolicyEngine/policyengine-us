from policyengine_us.model_api import *


class ok_liheap_countable_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Oklahoma LIHEAP countable personal income before deductions"
    defined_for = StateCode.OK
    # OAC 340:20-1-11(a)-(b). The same personal sources apply before
    # ordinary eligibility and before ineligible-member income deeming.
    reference = "https://prod-ok-administrativerules.tecuity.com/api/BlobStorageGetFile?storageContainer=TitleHtml&name=Title_340.html"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ok.dhs.liheap.income.sources
        income = person("ok_liheap_countable_earned_income", period)
        for source in p.unearned:
            # SSI is monthly; ADD annualizes it exactly once here. Other
            # listed streams are disjoint annual personal income inputs.
            income = income + max_(add(person, period, [source], options=[ADD]), 0)
        # Oklahoma TANF is an SPM aggregate and is counted separately once.
        return income
