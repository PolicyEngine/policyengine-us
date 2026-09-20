from policyengine_us.model_api import *


class tx_ccs_dfps_authorized(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    defined_for = StateCode.TX
    label = "Texas DFPS has authorized and funded protective child care"
    documentation = (
        "Whether DFPS has determined this child's eligibility and currently "
        "authorizes and funds protective-services child care under 40 TAC "
        "809.49. Court supervision or a care order alone is insufficient."
    )
    reference = "https://www.twc.texas.gov/sites/default/files/ogc/docs/rules-chapter-809-child-care-services-twc.pdf#page=30"
