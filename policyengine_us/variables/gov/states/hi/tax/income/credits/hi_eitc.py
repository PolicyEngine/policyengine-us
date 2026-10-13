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
    reference = (
        "https://www.capitol.hawaii.gov/hrscurrent/Vol04_Ch0201-0257/HRS0235/HRS_0235-0055_0007_0005.htm",
        # Form N-356, lines 10 to 13: the nonrefundable credit is limited to
        # the adjusted tax liability, "the amount from Form N-11, line 34"
        # (2018-2019 wording; 2020-2022 forms name the line "Adjusted Tax
        # Liability"). The 2018 form is no longer on files.hawaii.gov.
        "https://web.archive.org/web/20190819110547/https://files.hawaii.gov/tax/forms/2018/n356_i.pdf#page=1",
        "https://files.hawaii.gov/tax/forms/2022/n356_i.pdf#page=1",
    )

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.hi.tax.income.credits.non_refundable
        if "hi_eitc" not in ordered_credits:
            return tax_unit("hi_eitc_potential", period)

        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "hi_adjusted_tax_liability",
            "hi_eitc",
            "hi_eitc_potential",
        )
