from policyengine_us.model_api import *


class is_medicaid_lawfully_residing_option_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Medicaid under the lawfully residing children and pregnant individuals option"
    definition_period = YEAR
    # 42 USC 1396b(v)(4)(A), added by CHIPRA section 214, lets a state cover
    # lawfully residing children and pregnant individuals notwithstanding the
    # qualified-alien limit and the five-year bar (8 USC 1611(a) and 1613).
    # H.R.1 section 71109 leaves the option unchanged after October 1, 2026.
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396b#v_4_A",
        "https://downloads.cms.gov/cmsgov/archived-downloads/smdl/downloads/sho10006.pdf#page=3",
        "https://www.medicaid.gov/federal-policy-guidance/downloads/SHO-12-002.pdf#page=1",
        "https://www.medicaid.gov/federal-policy-guidance/downloads/sho21007.pdf#page=17",
        "https://www.medicaid.gov/federal-policy-guidance/downloads/sho26001.pdf#page=5",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.lawfully_residing
        status = person("immigration_status", period).decode_to_str()
        lawfully_residing = np.isin(status, p.immigration_statuses)
        state = person.household("state_code_str", period)
        age = person("age", period)
        child = p.child[state].astype(bool) & (age < p.child_age_limit[state])
        # The pregnancy category runs through the state's postpartum period, which
        # includes the 12-month extension where the state elected it (SHO #21-007).
        pregnant = p.pregnant[state].astype(bool) & person(
            "is_pregnant_for_medicaid_nfc", period
        )
        return lawfully_residing & (child | pregnant)
