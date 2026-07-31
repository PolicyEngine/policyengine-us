from policyengine_us.model_api import *


class medicaid_ltss_countable_resources(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS countable resources"
    unit = USD
    quantity_type = STOCK
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Trusted comprehensive LTSS countable-resource input for the "
        "applicant or applicant assistance unit after applicable state "
        "exclusions, disregards, and ownership rules. When the applicant has "
        "a community spouse, this input excludes resources allocated to that "
        "spouse, which are supplied separately. It is not calculated from "
        "PolicyEngine's narrower SSI asset inputs. The user must perform the "
        "resource inventory and legal classification before supplying this "
        "value."
    )
    reference = "https://www.law.cornell.edu/cfr/text/42/435.601"
