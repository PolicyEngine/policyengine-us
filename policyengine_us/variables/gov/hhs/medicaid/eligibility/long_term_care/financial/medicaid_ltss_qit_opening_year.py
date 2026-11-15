from policyengine_us.model_api import *


class medicaid_ltss_qit_opening_year(Variable):
    value_type = int
    entity = Person
    label = "Calendar year the Medicaid LTSS qualified income trust was opened"
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Calendar year in which the qualified income trust was established. "
        "Report this historical fact with medicaid_ltss_qit_opening_month "
        "in each modeled month. The default zero means that the opening "
        "date has not been reported. Texas permits a verified partial "
        "deposit to exclude the covered sources only in this opening month."
    )
    reference = "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/f-6800-qualified-income-trust"
