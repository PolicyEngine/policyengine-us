from policyengine_us.model_api import *


class or_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Oregon LIHEAP countable household income"
    unit = USD
    defined_for = StateCode.OR
    reference = "https://www.oregon.gov/ohcs/energy-weatherization/Documents/2026%20Final%20Energy%20Assistance%20Intake%20Operations%20%26%20Policy%20Manual.pdf#page=35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53"
    documentation = "Annual income approximates the allowed one-, three- or twelve-month observation window. Interest is assumed withdrawn. Unsupported details include regular gifts, foster and adoption payments, tribal receipts, work-study, private-disability Social Security offsets and caregiver payments within the household. Military wages should be included in employment_income. Use a direct countable-income override when these details matter."

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["or"].ohcs.liheap.income
        person = spm_unit.members
        interest = person("interest_income", period)
        counted_interest = spm_unit.sum(
            where(interest > p.interest_threshold, interest, 0)
        )
        return (
            add(spm_unit, period, ["or_liheap_countable_earned_income"])
            + add(spm_unit, period, p.sources.unearned)
            + counted_interest
        )
