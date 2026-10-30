from policyengine_us.model_api import *


class nm_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "New Mexico LIHEAP countable income"
    defined_for = StateCode.NM
    reference = (
        # 8.150.520.8 through 8.150.520.14 NMAC
        "https://www.srca.nm.gov/parts/title08/08.150.0520.html",
        # PDF pages 5-6
        "https://liheapch.acf.gov/docs/2026/state-plans/NM_Plan_2026.pdf#page=5",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nm.hca.liheap.income
        person = spm_unit.members
        # Annual inputs stand in for the gross income of the 30 days before
        # eligibility is determined, including its weekly x4 and biweekly x2
        # conversion. Gross earned income counts for members over the age of
        # 18 and gross unearned income for every member.
        earned_counted = person("age", period) > p.earned_income_age
        # Each source is floored at zero, so a loss in one source cannot
        # offset another.
        earned = 0
        for source in p.sources.earned:
            earned = earned + max_(person(source, period), 0)
        unearned = 0
        for source in p.sources.unearned:
            unearned = unearned + max_(person(source, period, options=[ADD]), 0)
        member_income = earned * earned_counted + unearned
        # The gross income of an ineligible non-citizen is divided by all
        # members, eligible and ineligible, and counted for the eligible
        # members only (8.150.520.10 B NMAC).
        eligible_member = person("is_citizen_or_legal_immigrant", period)
        eligible_share = spm_unit("nm_liheap_household_size", period) / spm_unit(
            "spm_unit_size", period
        )
        counted_income = where(
            eligible_member,
            member_income,
            member_income * spm_unit.project(eligible_share),
        )
        # TANF (New Mexico Works) is counted once at the SPM unit level
        # through the take-up-gated tanf total.
        return spm_unit.sum(counted_income) + spm_unit("tanf", period)
