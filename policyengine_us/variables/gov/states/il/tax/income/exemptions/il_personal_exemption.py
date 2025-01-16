from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.il.tax.income.exemptions.il_personal_exemption_eligibility_status import (
    ILPersonalExemptionEligibilityStatus,
)


class il_personal_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois personal exemption amount"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IL

    def formula(tax_unit, period, parameters):
        il_is_personal_exemption_eligible = tax_unit(
            "il_personal_exemption_eligibility_status", period
        )

        personal_exemption_amount = parameters(
            period
        ).gov.states.il.tax.income.exemption.personal

        return personal_exemption_amount * select(
            [
                il_is_personal_exemption_eligible
                == ILPersonalExemptionEligibilityStatus.BOTH_ELIGIBLE,
                il_is_personal_exemption_eligible
                == ILPersonalExemptionEligibilityStatus.PARTIALLY_ELIGIBLE,
            ],
            [2, 1],
            0,
        )
