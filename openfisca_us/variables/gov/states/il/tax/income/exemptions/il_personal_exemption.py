from openfisca_us.model_api import *


class il_personal_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL personal exemption amount"
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        il_is_personal_exemption_eligible = tax_unit(
            "il_personal_exemption_eligibility_status", period
        )

        eligibility_status = il_is_personal_exemption_eligible.possible_values

        personal_exemption_amount = parameters(
            period
        ).gov.states.il.tax.income.exemption.personal

        return select(
            [
                il_is_personal_exemption_eligible
                == eligibility_status.ELIGIBLE,
                il_is_personal_exemption_eligible
                == eligibility_status.PARTNER_INELIGIBLE,
                il_is_personal_exemption_eligible
                == eligibility_status.NOT_ELIGIBLE,
            ],
            [personal_exemption_amount * 2, personal_exemption_amount, 0],
        )
