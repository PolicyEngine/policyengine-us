from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.wi.dhs.ssp._wi_cts import (
    cts_relationships,
    cts_ssi_recipient,
)


class wi_cts_child_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin CTS nonfinancially eligible child"
    definition_period = MONTH
    reference = (
        "https://docs.legis.wisconsin.gov/document/statutes/49.775",
        # PDF pages 19-20
        "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf#page=19",
    )
    documentation = "Both co-resident parents named by parent IDs must receive Wisconsin state SSI. The Huber Law childcare-release exception (Handbook 3.1.6) is not modeled."

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wi.dhs.ssp.cts
        _, _, _, _, parents, ssi_parents = cts_relationships(person, period)
        status = person("immigration_status", period.this_year).decode_to_str()
        return (
            person("wi_cts_dependent_child", period)
            & ~cts_ssi_recipient(person, period)
            & (ssi_parents > 0)
            & (parents == ssi_parents)
            & (
                np.isin(status, p.eligible_immigration_statuses)
                | person("wi_cts_other_qualifying_immigration_status", period)
            )
            & ~person("is_incarcerated", period)
        )
