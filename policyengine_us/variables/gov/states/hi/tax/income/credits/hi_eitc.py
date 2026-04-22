from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class hi_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii earned income tax credit"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    reference = "https://www.capitol.hawaii.gov/hrscurrent/Vol04_Ch0201-0257/HRS0235/HRS_0235-0055_0075.htm"

    def formula(tax_unit, period, parameters):
        if period.start.year >= 2023:
            return tax_unit("hi_eitc_potential", period)

        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ["hi_eitc"],
            "hi_income_tax_before_non_refundable_credits",
            "hi_eitc",
            "hi_eitc_potential",
        )
