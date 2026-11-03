from policyengine_us.model_api import *


class wi_wheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Wisconsin WHEAP countable income"
    defined_for = StateCode.WI
    reference = (
        # Sections 3.3.2-3.3.5 and Tables 3.4-3.6.
        # PDF pages 45-63
        "https://web.archive.org/web/20260428215048/https://energyandhousing.wi.gov/Documents/WHEAP/WheapManual_PY26.pdf#page=45",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wi.doa.wheap.income
        person = spm_unit.members
        age = person("age", period)
        # Earned income of minors and of high school students 18 and older is
        # ignored; is_in_k12_school identifies the students.
        excluded = (age < p.adult_age) | person("is_in_k12_school", period)
        wages = 0
        for source in p.sources.earned:
            wages = wages + max_(person(source, period), 0)
        # Self-employment, rental and royalty profits and losses offset each
        # other across sources and members; a net loss counts as zero and
        # cannot offset other income.
        business = where(
            excluded, 0, add(person, period, p.sources.self_employment)
        ) + add(person, period, p.sources.rental)
        unearned = 0
        for source in p.sources.unearned:
            unearned = unearned + max_(person(source, period, options=[ADD]), 0)
        # All withdrawals count from age 73. Regular withdrawals before 73
        # also count but cannot be told apart from lump sums, which are
        # ignored as asset drawdowns.
        distributions = where(
            age >= p.retirement_distribution_age,
            max_(person("retirement_distributions", period), 0),
            0,
        )
        # Social Security and Railroad Retirement count net of Medicare
        # premiums; Part C and Part D premiums have no input.
        retirement_benefits = max_(person("social_security", period), 0) + max_(
            person("railroad_benefits", period), 0
        )
        net_retirement_benefits = max_(
            retirement_benefits - person("medicare_part_b_premium", period), 0
        )
        investment = 0
        for source in p.sources.investment:
            investment = investment + max_(person(source, period), 0)
        counted_investment = where(investment >= p.investment_minimum, investment, 0)
        personal = (
            where(excluded, 0, wages)
            + unearned
            + distributions
            + net_retirement_benefits
            + counted_investment
        )
        net_business = max_(spm_unit.sum(business), 0)
        # W-2 cash grants count; unemployment compensation is ignored.
        w2_cash = max_(spm_unit("tanf", period), 0)
        deductions = add(spm_unit, period, p.deductions)
        # Annual amounts approximate the prior-month test period. The extra
        # paycheck rule, the present-month option and tribal per capita
        # payments are not modeled.
        return max_(spm_unit.sum(personal) + net_business + w2_cash - deductions, 0)
