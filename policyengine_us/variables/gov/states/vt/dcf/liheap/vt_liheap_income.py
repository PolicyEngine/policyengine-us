from policyengine_us.model_api import *


class vt_liheap_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Vermont LIHEAP gross household income"
    defined_for = StateCode.VT
    reference = (
        # PDF pages 10, 25-29, 34
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2900-Seasonal-Fuel-Assistance.pdf#page=10",
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/ESD-Procedure-P2910.pdf",
        "https://legislature.vermont.gov/statutes/section/33/026/02604",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.vt.dcf.liheap.income
        person = spm_unit.members
        # Gross income of all members, regardless of immigration status, with no
        # deductions (rule 2910(a); P-2910). Annual income approximates the
        # 30-day lookback of rule 2911(c). Each source is floored at zero, so a
        # loss in one source cannot offset another and the total is never
        # negative.
        earned = 0
        for source in p.sources.earned:
            earned = earned + max_(person(source, period), 0)
        unearned = 0
        for source in p.sources.unearned:
            # add() also sums monthly sources such as vt_aabd over the year.
            unearned = unearned + max_(add(person, period, [source]), 0)
        # Rule 2912(a)(12) excludes the earnings of a member under 18 who lives
        # with a parent or under parental control and attends elementary, high
        # school, home school or GED classes at least half time. K-12 enrollment
        # stands in for that schooling and tax-unit dependency for parental
        # control.
        age = person("age", period)
        excluded_child = (
            (age < p.child_earnings_age_limit)
            & person("is_in_k12_school", period)
            & person("is_tax_unit_dependent", period)
        )
        counted_earned = where(excluded_child, 0, earned)
        # Reach Up is counted once through the SPM-unit tanf aggregate.
        return spm_unit.sum(counted_earned + unearned) + spm_unit("tanf", period)
