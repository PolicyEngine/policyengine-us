from policyengine_us.model_api import *


class oh_personal_exemptions_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Ohio Personal Exemptions Eligibility"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=14",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        dependent_on_another_return = tax_unit(
            "head_is_dependent_elsewhere", period
        )
        return ~dependent_on_another_return
