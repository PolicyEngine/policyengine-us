from policyengine_us.model_api import *


class oh_personal_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio Personal Exemptions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=14",
    )
    defined_for = "oh_personal_exemptions_eligible"
