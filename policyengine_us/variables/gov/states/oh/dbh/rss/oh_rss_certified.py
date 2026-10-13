from policyengine_us.model_api import *


class oh_rss_certified(Variable):
    value_type = bool
    entity = Person
    label = "Ohio RSS certified care placement"
    definition_period = MONTH
    documentation = "Ohio has approved the current RSS placement and protective level of care, including the facility, supervision, waiver, PACE, hospice and provider-relationship conditions in rule 5122-36-02. Includes a state-approved temporary institutional continuation under 5160:1-5-01(H)."
    reference = (
        "https://codes.ohio.gov/ohio-administrative-code/rule-5122-36-02",
        "https://codes.ohio.gov/ohio-administrative-code/rule-5160:1-5-01",
    )
