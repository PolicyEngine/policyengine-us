from policyengine_us.model_api import *


class railroad_disability_benefits(Variable):
    value_type = float
    entity = Person
    label = "Railroad Retirement disability annuity amount"
    unit = USD
    definition_period = YEAR
    default_value = 0
    documentation = (
        "Annual gross amount the Railroad Retirement Board pays on the basis "
        "of disability. Include this amount in railroad_benefits."
    )
    reference = "https://idjj.illinois.gov/content/dam/soi/en/web/idjj/documents/register-volume45-issue-29.pdf#page=419"
