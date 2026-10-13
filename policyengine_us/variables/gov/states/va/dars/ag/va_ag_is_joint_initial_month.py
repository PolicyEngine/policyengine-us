from policyengine_us.model_api import *


class va_ag_is_joint_initial_month(Variable):
    value_type = bool
    entity = Person
    label = "Virginia Auxiliary Grant couple in the initial month"
    definition_period = MONTH
    default_value = False
    # PDF pages 34-35
    reference = "https://townhall.virginia.gov/l/GetFile.cfm?File=C:%5CTownHall%5Cdocroot%5CGuidanceDocs%5C262%5CGDoc_DARS_5346_v2.pdf#page=34"
    documentation = """
    Set for both spouses only in the initial application month when both lived
    together at the start of the month, entered approved care, applied, and
    were found eligible that month. In later months each spouse is a separate
    case and a spouse's income is not deemed. Represent that in the federal SSI
    inputs: set ssi_claim_is_joint to false when both spouses are SSI-eligible;
    otherwise use separate marital units or set is_ssi_spousal_deeming_applies
    to false for the recipient.
    """
