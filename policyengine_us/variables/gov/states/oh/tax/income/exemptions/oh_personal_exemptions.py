from policyengine_us.model_api import *


class oh_personal_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio Personal Exemption Eligibility"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=14",
    )
    defined_for = "oh_personal_exemptions_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.oh.tax.income.exemptions.personal

        count = tax_unit("exemptions_count", period)

        agi = tax_unit("oh_agi", period)
        credit_amount = p.amount.calc(agi)

        return count * credit_amount
