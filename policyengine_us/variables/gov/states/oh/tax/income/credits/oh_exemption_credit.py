from policyengine_us.model_api import *


class oh_exemption_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio Exemption Credit"
    unit = USD
    definition_period = YEAR
    reference = ("https://codes.ohio.gov/ohio-revised-code/section-5747.022")
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        agi = tax_unit("oh_agi", period)
        exemptions = tax_unit("exemptions", period)
        p = parameters(period).gov.states.oh.tax.income.credits.exemption
        credit_amount = exemptions * p.amount
        modified_agi = agi - credit_amount
        agi_eligible = modified_agi < p.income_threshold

        return credit_amount * agi_eligible
