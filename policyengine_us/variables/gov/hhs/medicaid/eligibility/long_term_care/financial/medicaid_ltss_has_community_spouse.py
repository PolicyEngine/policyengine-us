from policyengine_us.model_api import *


class medicaid_ltss_has_community_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Has a community spouse for Medicaid LTSS"
    definition_period = MONTH
    default_value = False
    documentation = (
        "Explicit indication that the LTSS applicant has a community spouse "
        "for spousal-impoverishment protections. It is not inferred from a "
        "tax, household, or marital unit."
    )
    reference = "https://www.law.cornell.edu/uscode/text/42/1396r-5"
