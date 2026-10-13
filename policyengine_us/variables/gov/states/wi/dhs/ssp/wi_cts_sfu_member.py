from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.wi.dhs.ssp._wi_cts import cts_filing_unit


class wi_cts_sfu_member(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin CTS standard filing unit member before Buening"
    definition_period = MONTH
    # PDF pages 18, 30, 68-75
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf#page=18"
    documentation = "Co-resident parent IDs group non-SSI dependent children who share a parent, with those parents, into separate filing units; an SSI child does not link its siblings. Without parent links the family is treated as one nuclear family. Override to remove a person from their unit, for example a step-parent: parent IDs do not distinguish natural or adoptive parents from step-parents. A person outside every unit cannot be added."

    def formula(person, period, parameters):
        _, member, _ = cts_filing_unit(person, period)
        return member
