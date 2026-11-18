from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.wi.dhs.ssp._wi_cts import cts_filing_unit


class wi_cts_buening_member(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin CTS non-SSI co-parent subgroup member"
    definition_period = MONTH
    # PDF pages 33-34
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf#page=33"
    documentation = "The non-SSI co-parent and children whose needs must be tested separately under Buening. Requires parent IDs."

    def formula(person, period, parameters):
        _, _, subgroup = cts_filing_unit(person, period)
        return subgroup
