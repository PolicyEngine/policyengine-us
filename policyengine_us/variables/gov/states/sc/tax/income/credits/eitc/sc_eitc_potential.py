from policyengine_us.model_api import *


class sc_eitc_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina EITC"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.sc.gov/forms-site/Forms/TC60_2021.pdf",
        "https://www.scstatehouse.gov/sess126_2025-2026/bills/4216.htm",
    )
    defined_for = StateCode.SC

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("eitc", period)
        p = parameters(period).gov.states.sc.tax.income.credits.eitc
        uncapped = np.round(federal_eitc * p.rate, 1)
        # Apply cap (infinite before 2026, $200 from 2026+)
        return min_(uncapped, p.max)
