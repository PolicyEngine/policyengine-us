from policyengine_us.model_api import *


class oh_exemption_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio Exemption Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        agi = tax_unit("oh_agi", period)
        exemption_count = tax_unit("tax_unit_size", period)

        p = parameters(period).gov.states.oh.tax.income
        personal_exemption_amount = p.credits.exemption.amount.calc(agi)
        modified_agi = agi - personal_exemption_amount * exemption_count
        income_eligible = modified_agi < p.credits.exemption.income_limit
        credit_amount = p.credits.exemption.credit_amount
        return income_eligible * exemption_count * credit_amount
