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
        # Per form instructions, only certain income sources must be
        # floored at 0 if negative. Capital gains have special loss limitation.
        income_sources = p.household_resources

        # Sources that must be floored at 0 per form instructions:
        # "Net business income (including net farm income). If negative, enter 0"
        # "Net royalty or rent income. If negative, enter 0"
        floored_sources = {
            "farm_income",
            "self_employment_income",
            "partnership_s_corp_income",
            "rental_income",
            "farm_rent_income",
        }

        # Iterate through each source, applying flooring only to
        # sources that require it per form instructions
        total = 0
        for source in income_sources:
            if source in floored_sources:
                # Per MI-1040CR instructions: "If negative, enter 0"
                total += max_(add(tax_unit, period, [source]), 0)
            else:
                # Other sources are added as-is without flooring
                total += add(tax_unit, period, [source])

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
