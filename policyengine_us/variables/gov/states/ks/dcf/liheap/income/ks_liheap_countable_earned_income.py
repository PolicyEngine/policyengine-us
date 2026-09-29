from policyengine_us.model_api import *


class ks_liheap_countable_earned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Kansas LIEAP countable earned income"
    documentation = (
        "Gross wages and reported net self-employment income of adults. "
        "Using net business income directly approximates KEESM 13360's gross "
        "receipts less a 25% expense deduction or elected allowable actual "
        "costs; no additional expense deduction is applied to net income. "
        "Each income source is floored at zero, so business losses do not "
        "offset other earnings. Earned income of children under 18 is excluded. "
        "Supply countable earned income directly when the exact Kansas "
        "self-employment amount is known."
    )
    unit = USD
    reference = (
        "https://content.dcf.ks.gov/ees/KEESM/Robo10-24/Robo_10_01_24/keesm13360.htm",
        "https://content.dcf.ks.gov/ees/KEESM/Robo01-26/Robo_01_01_26/keesm13360.htm",
        "https://liheapch.acf.gov/docs/2026/state-plans/KS_Plan_2026.pdf#page=6",
        "https://liheapch.acf.gov/docs/2026/state-plans/KS_Plan_2026.pdf#page=7",
    )
    defined_for = StateCode.KS

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ks.dcf.liheap.income
        earned = 0
        for source in p.sources.earned:
            earned = earned + max_(person(source, period), 0)
        age = person("age", period)
        return where(age >= p.earned_income_min_age, earned, 0)
