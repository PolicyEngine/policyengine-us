from policyengine_us.model_api import *


class nyc_school_tax_credit_fixed_amount_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for NYC School Tax Credit Fixed Amount"
    definition_period = YEAR
    defined_for = "in_nyc"
    reference = (
        # NY Tax Law § 606(ggg)(2), (4-a)
        "https://www.nysenate.gov/legislation/laws/TAX/606",
        "https://www.tax.ny.gov/pdf/2025/inc/it201i_2025.pdf#page=20",
    )

    def formula(tax_unit, period, parameters):
        # § 606(ggg)(4-a) denies the fixed amount to any taxpayer with income,
        # as defined in § 606(ggg)(2), over the limit.

        # Get the NYC School Tax Credit Fixed Amount part of the parameter tree.
        p = parameters(period).gov.local.ny.nyc.tax.income.credits.school.fixed

        # Get income that counts towards the NYC School Tax Credit.
        nyc_stc_income = tax_unit("nyc_school_credit_income", period)

        # A filer who can be claimed as a dependent does not qualify (IT-201
        # line 69). Form NYC-210 asks about each spouse and allows "the credit
        # amount of the eligible spouse" when only one qualifies.
        independent_filers = tax_unit(
            "head_spouse_count_not_dependent_elsewhere", period
        )
        return (nyc_stc_income <= p.income_limit) & (independent_filers > 0)
