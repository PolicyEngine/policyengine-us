from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.wi.dhs.ssp._wi_cts import cts_filing_unit


class wi_cts_sfu_member(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin CTS standard filing unit member before Buening"
    definition_period = MONTH
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf"
    documentation = "Uses co-resident parent IDs to form the target-child sibling and parent group. Without parent links the family is treated as one nuclear family. Override for multigeneration, step-parent or other complex filing units; parent IDs do not distinguish natural/adoptive from step relationships."

    def formula(person, period, parameters):
        members, _ = cts_filing_unit(person, period)
        return members
