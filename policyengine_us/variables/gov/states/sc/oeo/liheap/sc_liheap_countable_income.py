from policyengine_us.model_api import *


class sc_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina LIHEAP annual countable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = (
        # PDF pages 5-6
        "https://oeo.sc.gov/managedsites/prd/oeo/documents/2026%20LIHEAP%20State%20Plan.pdf#page=5",
        "https://oeo.sc.gov/managedsites/prd/oeo/documents/2026%20South%20Carolina%20LIHEAP%20Model%20Plan%20w%20Attachments.pdf#page=529",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.oeo.liheap.income
        person = spm_unit.members
        # Existing net business inputs approximate self-employment receipts
        # without a second expense deduction. Annual flows approximate 30 days.
        earned = 0
        for source in p.earned_sources:
            earned = earned + max_(person(source, period), 0)
        unearned = 0
        for source in p.unearned_sources:
            unearned = unearned + max_(add(person, period, [source]), 0)
        # OEO's 2024 guide calculates no income under age 18 apart from Social Security
        # or disability income. Legal settlements and earmarked receipts lack inputs.
        minor_income = 0
        for source in p.minor_unearned_sources:
            minor_income = minor_income + max_(add(person, period, [source]), 0)
        adult = person("age", period) >= p.adult_min_age
        income = where(adult, earned + unearned, minor_income)
        # State-placed foster children are not household members.
        foster = person("is_in_foster_care", period.first_month)
        return spm_unit.sum(where(foster, 0, income))
