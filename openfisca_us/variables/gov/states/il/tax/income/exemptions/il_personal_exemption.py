from openfisca_us.model_api import *


class il_personal_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL personal exemption amount"
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        il_is_personal_exemption_eligible = tax_unit("il_personal_exemption_eligibility_status", period)
        personal_exemption_amounts = parameters(
            period
        ).gov.states.il.tax.income.exemption.personal

        return personal_exemption_amounts[il_is_personal_exemption_eligible]
