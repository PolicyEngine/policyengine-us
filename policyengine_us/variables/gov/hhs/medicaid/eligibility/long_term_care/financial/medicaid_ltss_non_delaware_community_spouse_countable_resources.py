from policyengine_us.model_api import *


class medicaid_ltss_non_delaware_community_spouse_countable_resources(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS community spouse resources outside Delaware"
    unit = USD
    quantity_type = STOCK
    definition_period = MONTH
    default_value = 0
    documentation = (
        "The community spouse's own current comprehensive countable-resource "
        "inventory for applicants outside Delaware whose community spouse "
        "is outside the simulation, after applicable ownership and exclusion "
        "rules. A represented spouse's own "
        "medicaid_ltss_individual_countable_resources in the two-person "
        "marital unit takes precedence in Texas and Washington as well as "
        "Delaware. This fallback is read only for a community-spouse "
        "applicant in a singleton marital unit outside Delaware. "
        "Keeping this input separate from the derived community-spouse "
        "resource output permits mixed-state populations without overriding "
        "Delaware's calculation."
    )
    reference = "https://www.law.cornell.edu/uscode/text/42/1396r-5"
