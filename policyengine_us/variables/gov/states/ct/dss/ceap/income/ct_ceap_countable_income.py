from policyengine_us.model_api import *


class ct_ceap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut CEAP countable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/CT_Plan_2026.pdf#page=6,7",
        "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/winter-heating-assistance/09012026/ffy-27-liheap-allocation-plan.pdf#page=5,8,9",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.ceap.income
        person = spm_unit.members
        # Annual inputs approximate the permitted 52-week assessment. Existing
        # net business inputs are used without further business-cost deductions.
        earned = sum(max_(person(source, period), 0) for source in p.sources.earned)
        adult = person("age", period) >= p.earned_income_min_age
        member = ~person("is_in_foster_care", period.first_month)
        unearned = add(person, period, p.sources.unearned)
        # Nonqualified members' income counts in full. SSI, TFA and general
        # assistance are excluded by the model plan's income checklist.
        # Medicare premiums, excluded VA pension subtypes, gross rental receipts,
        # in-kind support and separately identified jury/settlement/insurance/
        # AmeriCorps receipts cannot be resolved by these existing income inputs.
        return max_(spm_unit.sum(member * (where(adult, earned, 0) + unearned)), 0)
