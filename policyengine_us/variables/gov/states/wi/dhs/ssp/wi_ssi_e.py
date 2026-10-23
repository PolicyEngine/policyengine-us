from policyengine_us.model_api import *


class wi_ssi_e(Variable):
    value_type = float
    entity = Person
    label = "Wisconsin SSI Exceptional Expense Supplement"
    definition_period = MONTH
    unit = USD
    defined_for = "wi_ssp_eligible"
    reference = (
        "https://www.dhs.wisconsin.gov/dms/memos/ops/dms-ops-2026-12.pdf#page=2",
        "https://docs.legis.wisconsin.gov/document/statutes/49.77",
        "https://www.emhandbooks.wisconsin.gov/ssi-admin/3/3.1_state-only_ssi_recipients.htm",
        # PDF pages 10, 13, 18
        "https://www.dhs.wisconsin.gov/publications/p20679-26-01.pdf#page=10",
    )

    # Grandfathered state-only awards remain outside this formula. DMS Operations
    # Memo 26-12 establishes a 10% increase to an existing April 2026 award.
    # The references are unclear about a NEW SSI-E certification: whether
    # to add E to the protected regular award or recompute a combined
    # income budget, and how any historical floor or cap carries forward.
    # Wis. Stat. 49.77(2)(a)3, (3s), (5) and Handbook 3.1 establish eligibility
    # and payment standards, but do not specify that calculation sequence.

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wi.dhs.ssp.exceptional_expense
        # Recipients in the "household of another" (one-third reduction)
        # arrangement are not eligible for SSI-E (P-20679 3.1.1).
        arrangement = person("ssi_federal_living_arrangement", period)
        household_of_another = (
            arrangement == arrangement.possible_values.ANOTHER_PERSONS_HOUSEHOLD
        )
        certified = (
            person("wi_ssi_e_certified", period)
            & person("wi_ssp_eligible", period)
            & ~household_of_another
        )
        both = person.marital_unit.sum(certified) == 2
        return certified * where(both, p.couple / 2, p.individual)
