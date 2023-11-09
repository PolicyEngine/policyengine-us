from policyengine_us.model_api import *


class oh_exemption_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio Exemption Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://codes.ohio.gov/ohio-revised-code/section-5747.022"
    defined_for = "oh_exemption_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.oh.tax.income.exemptions

        count = tax_unit("exemptions_count", period)

        return credit_amount * count
