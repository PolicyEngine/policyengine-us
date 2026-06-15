from policyengine_us.model_api import *


class fl_sr_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Florida School Readiness countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.FL
    reference = (
        "https://www.flsenate.gov/laws/statutes/2025/1002.81",
        "https://www.elcduval.org/wp-content/uploads/2025/07/Rule-6M-4.400_Frequently-Asked-Questions.pdf#page=1",
        "https://flrules.elaws.us/fac/6m-4.200",
    )

    def formula(spm_unit, period, parameters):
        sources = parameters(period).gov.states.fl.doe.sr.income.sources
        person = spm_unit.members
        # Fla. Stat. 1002.81(7): family income is the combined gross income
        # (earned or unearned) of household members who are 18 or older; income
        # of members under 18 is excluded. (The statute's further exclusions for
        # still-enrolled high-school students 18+ and disabled students under 22
        # are not modeled at the moment.) 6M-4.400 FAQ Q6: gross income, no
        # School Readiness disregards.
        is_adult = ~person("is_child", period.this_year)
        income_per_person = add(person, period, sources)
        return spm_unit.sum(income_per_person * is_adult)
