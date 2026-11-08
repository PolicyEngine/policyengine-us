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
        "maintenance or interest and dividends. Each unearned source counts "
        "for each person at no less than zero, so a rental loss does not "
        "offset other income. The $20 general, $65 earned and one-half "
        "earned income exclusions apply once to the combined income. Not "
        "modeled: the Social Security cost-of-living increase, which SSA "
        "leaves out through the month after the new poverty guidelines are "
        "published (20 CFR 418.3340(f)); the model counts the year's "
        "benefits in full."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1395w-114#a_3_C",
        "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-423/subpart-P/section-423.772",
        "https://www.ecfr.gov/current/title-20/chapter-III/part-418/subpart-D/section-418.3310",
        "https://www.ecfr.gov/current/title-20/chapter-III/part-418/subpart-D/section-418.3325",
        "https://www.ecfr.gov/current/title-20/chapter-III/part-418/subpart-D/section-418.3335",
        "https://www.ecfr.gov/current/title-20/chapter-III/part-418/subpart-D/section-418.3340#p-418.3340(f)",
        "https://www.ecfr.gov/current/title-20/chapter-III/part-418/subpart-D/section-418.3350",
        "https://secure.ssa.gov/poms.nsf/lnx/0603020050",
        "https://secure.ssa.gov/poms.nsf/lnx/0500830505",
    )

    def formula(person, period, parameters):
        p = parameters(period)
        excluded = p.gov.hhs.medicare.part_d.low_income_subsidy.income.excluded_sources
        # SSI's unearned income sources without the ones the subsidy excludes,
        # so a change to SSI's list carries through and an excluded source is
        # never subtracted when SSI no longer counts it.
        sources = [
            source
            for source in p.gov.ssa.ssi.income.sources.unearned
            if source not in excluded
        ]
        # SSI counts net rental income, and expenses above the rent do not
        # offset other income (POMS SI 00830.505), so no source counts below
        # zero, for either spouse.
        unearned = person.filled_array(0.0)
        for source in sources:
            unearned = unearned + max_(person(source, period), 0)
        earned = person("ssi_earned_income", period)
        # A spouse's income counts whether or not the spouse applies or is
        # eligible, and the exclusions apply once to the couple's income.
        couple_earned = person.marital_unit.sum(earned)
        couple_unearned = person.marital_unit.sum(unearned)
        return _apply_ssi_exclusions(couple_earned, couple_unearned, parameters, period)
