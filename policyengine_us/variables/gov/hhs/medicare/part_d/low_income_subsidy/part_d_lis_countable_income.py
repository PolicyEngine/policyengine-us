from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class part_d_lis_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Medicare Part D low-income subsidy countable income"
    documentation = (
        "Annual countable income for the Part D low-income subsidy: the "
        "Supplemental Security Income definition of income, for the person "
        "and a spouse living with them, without in-kind support and "
        "maintenance or interest and dividends. The $20 general, $65 earned "
        "and one-half earned income exclusions apply once to the combined "
        "income."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1395w-114#a_3_C",
        "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-423/subpart-P/section-423.772",
        "https://www.ecfr.gov/current/title-20/chapter-III/part-418/subpart-D/section-418.3310",
        "https://www.ecfr.gov/current/title-20/chapter-III/part-418/subpart-D/section-418.3325",
        "https://www.ecfr.gov/current/title-20/chapter-III/part-418/subpart-D/section-418.3350",
        "https://secure.ssa.gov/poms.nsf/lnx/0603020050",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicare.part_d.low_income_subsidy.income
        earned = person("ssi_earned_income", period)
        unearned = person("ssi_unearned_income", period) - add(
            person, period, p.excluded_sources
        )
        # A spouse's income counts whether or not the spouse applies or is
        # eligible, and the exclusions apply once to the couple's income.
        couple_earned = person.marital_unit.sum(earned)
        couple_unearned = max_(person.marital_unit.sum(unearned), 0)
        return _apply_ssi_exclusions(couple_earned, couple_unearned, parameters, period)
