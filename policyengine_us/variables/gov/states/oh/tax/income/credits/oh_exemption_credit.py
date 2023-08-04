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
        exemptions = tax_unit("exemptions", period)
        p = parameters(period).gov.states.oh.tax.income.credits
        agi_eligible = agi < p.exemption.income_threshold
        credit_amount = exemptions * p.exemption.amount
        return credit_amount * agi_eligible
