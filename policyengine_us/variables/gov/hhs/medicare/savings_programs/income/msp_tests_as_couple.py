from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicare.savings_programs.income._msp_spouse_income import (
    msp_spouse_income,
    msp_spouses_combine_income,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


class msp_tests_as_couple(Variable):
    value_type = bool
    entity = Person
    label = "Medicare Savings Program tests this person as a couple"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396d#p",
        "https://www.law.cornell.edu/cfr/text/20/416.414",
        "https://www.law.cornell.edu/cfr/text/20/416.1160",
        "https://www.law.cornell.edu/cfr/text/20/416.1163",
        "https://www.law.cornell.edu/cfr/text/20/416.1801",
        "https://secure.ssa.gov/poms.nsf/lnx/0500501154",
    )
    documentation = """
    Whether SSI's spouse rules count a spouse's income for this person, which also
    makes the two-person poverty guideline the income limit. That holds when both
    spouses are on Medicare, when they are an eligible couple, or when the spouse's
    income after allocations for ineligible children is more than the difference
    between the couple and individual benefit rates (20 CFR 416.1163(d)(2)). If it
    is not more, nothing is deemed (416.1163(d)(1)). A medical treatment facility
    that separates a couple also leaves each spouse tested alone (416.414(b)(3)),
    unless both are on Medicare, when the model still tests them together. A person
    with no co-resident spouse (_ssi_spouse_index) is always tested alone.
    """

    def formula(person, period, parameters):
        year = period.this_year
        spouse = _ssi_spouse_index(person, year)
        spouse_earned, spouse_unearned = msp_spouse_income(person, year, spouse)
        p = parameters(period).gov.ssa.ssi.amount
        rate_difference = (p.couple - p.individual) * MONTHS_IN_YEAR
        spouse_income_is_deemed = spouse_earned + spouse_unearned > rate_difference
        split_by_facility = person("ssi_claim_is_joint", year) & ~person(
            "ssi_couple_computation_applies", period
        )
        return msp_spouses_combine_income(person, period, spouse) | (
            spouse_income_is_deemed & ~split_by_facility
        )
