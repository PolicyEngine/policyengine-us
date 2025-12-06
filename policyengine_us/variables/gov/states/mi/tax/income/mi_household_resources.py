from policyengine_us.model_api import *


class mi_household_resources(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan household resources"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI
    reference = (
        "https://law.justia.com/codes/michigan/2022/chapter-206/"
        "statute-act-281-of-1967/division-281-1967-1/division-281-1967-1-9/"
        "section-206-508/",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/"
        "Forms/IIT/TY2024/BOOK_MI-1040CR-7.pdf",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mi.tax.income
        # Per MI-1040CR-7 instructions, income sources must be floored at 0
        # if negative, except capital gains which are limited to the federal
        # loss limit ($3,000 for most filers, $1,500 for MFS).
        income_sources = p.household_resources
        total = 0
        for source in income_sources:
            if source == "net_capital_gains":
                # Use loss-limited capital gains per MI-1040CR-7 Line 24
                # instructions: losses cannot exceed $3,000 ($1,500 MFS)
                total += add(
                    tax_unit, period, ["loss_limited_net_capital_gains"]
                )
            else:
                # Per MI-1040CR-7 instructions, if negative enter 0
                total += max_(add(tax_unit, period, [source]), 0)

        health_insurance_premiums = add(
            tax_unit, period, ["health_insurance_premiums"]
        )
        above_the_line_deductions = tax_unit(
            "above_the_line_deductions", period
        )
        return max_(
            0,
            total - health_insurance_premiums - above_the_line_deductions,
        )
