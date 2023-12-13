from policyengine_us.model_api import *


class oh_distribution_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Ohio lump sum distribution eligibility"
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=29",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.oh.tax.income.credits
        distribution_received = (
            tax_unit("form_4972_lumpsum_distributions", period) > 0
        )
        agi_eligible = tax_unit("oh_modified_agi", period) < p.exemptions_cap

        return distribution_received & agi_eligible
