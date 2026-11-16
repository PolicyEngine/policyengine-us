from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._couple_standard import (
    uses_couple_standard,
)


class medicaid_optional_senior_or_disabled_uses_couple_standard(Variable):
    value_type = bool
    entity = Person
    label = "Uses the couple standard in Medicaid's aged, blind and disabled pathway"
    documentation = (
        "Whether a married person is tested as a couple, on combined income "
        "against the couple standard. SSI's rule applies by default (42 CFR "
        "435.601(b)): an applicant with an ineligible spouse is tested alone "
        "unless the spouse's income is deemed (20 CFR 416.1163(d)). The state "
        "parameters budgets_couple_together and couple_limit_without_deeming "
        "record the states whose own rules differ. Spouses split by a facility "
        "are each tested alone."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.601",
        "https://www.law.cornell.edu/cfr/text/42/435.602",
        "https://www.law.cornell.edu/cfr/text/20/416.1163",
        "https://www.law.cornell.edu/cfr/text/20/416.414",
        "https://www.law.cornell.edu/uscode/text/42/1396r-5",
    )

    def formula(person, period, parameters):
        state = person.household("state_code_str", period)
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled.income
        return uses_couple_standard(
            person,
            period,
            p.budgets_couple_together[state].astype(bool),
            p.couple_limit_without_deeming[state].astype(bool),
        )
