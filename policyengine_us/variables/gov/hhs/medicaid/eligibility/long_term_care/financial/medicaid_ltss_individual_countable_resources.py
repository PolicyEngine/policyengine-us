from policyengine_us.model_api import *


class medicaid_ltss_individual_countable_resources(Variable):
    value_type = float
    entity = Person
    label = "Individual Medicaid LTSS countable resources"
    unit = USD
    quantity_type = STOCK
    definition_period = MONTH
    default_value = 0
    documentation = (
        "The person's own comprehensive LTSS countable-resource inventory "
        "after applicable asset exclusions and legal ownership attribution, "
        "before assistance-unit aggregation or a community spouse resource "
        "allowance. Each spouse supplies their own resources; the model "
        "combines them when a couple budget applies. This is not calculated "
        "from PolicyEngine's narrower SSI asset inputs. Resource inventory "
        "and legal asset classification remain caller-supplied facts."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.601",
        "https://www.law.cornell.edu/cfr/text/42/435.602",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=67",
    )
