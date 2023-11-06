from policyengine_us.model_api import *


class de_elderly_or_disabled_income_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware aged or disabled exclusion"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-01_PaperInteractive.pdf#page=1"
    defined_for = "de_elderly_or_disabled_income_exclusion_eligible"

    def formula(tax_unit, period, parameters):
        # First get their filing status.
        filing_status = tax_unit("filing_status", period)
        p = parameters(
            period
        ).gov.states.de.tax.income.subtractions.exclusions.elderly_or_disabled

        return p.amount[filing_status]
