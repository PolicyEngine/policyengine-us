from policyengine_us.model_api import *


class oh_rss_certified(Variable):
    value_type = bool
    entity = Person
    label = "Ohio RSS certified care placement"
    definition_period = MONTH
    documentation = "Ohio has approved the current RSS placement and protective level of care, including the facility, supervision, waiver, PACE, hospice and provider-relationship conditions in rule 5122-36-02. Includes a state-approved temporary institutional continuation under 5160:1-5-01(H). Spouses are budgeted together only when they live in the same RSS living arrangement. Enter spouses who live apart as separate marital units from the month after they stop living together; marital units cannot change between months of one calculation."
    reference = (
        "https://codes.ohio.gov/ohio-administrative-code/rule-5122-36-02",
        "https://codes.ohio.gov/ohio-administrative-code/rule-5160:1-5-01",
        "https://codes.ohio.gov/ohio-administrative-code/rule-5160:1-3-05.20",
    )
    # NOTE: No microdata input sets this, so oh_rss is 0 in microsimulation and
    # reaches household calculations only.
