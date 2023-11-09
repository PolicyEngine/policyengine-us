from policyengine_us.model_api import *


class oh_exemption_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Ohio Exemption Credit Eligibility"
    definition_period = YEAR
    reference = "https://codes.ohio.gov/ohio-revised-code/section-5747.022"
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.oh.tax.income.exemptions

        agi = tax_unit("oh_agi", period)
        personal_exemptions = tax_unit("oh_personal_exemption", period)
        modified_agi = agi - personal_exemptions

        return modified_agi < p.income_threshold
