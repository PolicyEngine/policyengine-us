from openfisca_us.model_api import *


class ma_income_tax_exemption_threshold(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA income tax exemption threshold"
    unit = USD
    documentation = "MA AGI threshold below which an individual is exempt from State income tax."
    definition_period = YEAR
    reference = "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section5"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        dependents = tax_unit("tax_unit_dependents", period)
        tax = parameters(period).gov.states.ma.tax.income
        exempt_status = tax.exempt_status.limit
        personal_exemptions_added = (
            exempt_status.personal_exemption_added[filing_status]
            * tax.exemptions.personal[filing_status]
        )
        return (
            exempt_status.base[filing_status]
            + dependents * tax.exemptions.dependent
            + personal_exemptions_added
        )
