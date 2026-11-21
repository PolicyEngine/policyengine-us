from policyengine_us.model_api import *


class ri_rimap_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Rhode Island Marketplace Affordability Program"
    definition_period = YEAR
    defined_for = StateCode.RI
    reference = (
        "https://webserver.rilegislature.gov/statutes/TITLE42/42-157.2/42-157.2-4.htm",
        "https://healthsourceri.com/wp-content/uploads/2027-RIMAP-Final-Parameters.pdf#page=3",
    )
    documentation = (
        "Whether the tax unit qualifies for the Rhode Island Marketplace "
        "Affordability Program under either rule: below 200% of the federal "
        "poverty line with the federal premium tax credit, or above 400% "
        "when income is the only bar to that credit."
    )

    def formula(tax_unit, period, parameters):
        return tax_unit("ri_rimap_low_income_eligible", period) | tax_unit(
            "ri_rimap_high_income_eligible", period
        )
