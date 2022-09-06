from openfisca_us.model_api import *


class or_regular_exemptions(Variable):
    value_type = int
    entity = TaxUnit
    label = "OR regular exemptions"
    definition_period = YEAR
    # TODO: update
    reference = (
        "https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=18",
        "https://www.oregonlegislature.gov/bills_laws/ors/ors315.html",  # Subsection 315.266
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        federal_exemptions = tax_unit("exemptions", period)
        federal_agi = tax_unit("adjusted_gross_income", period)
        p = parameters(period).gov.states["or"].tax.income.credits.exemption
        qualifies = federal_agi <= p.income_limit.regular[filing_status]
        return qualifies * federal_exemptions
