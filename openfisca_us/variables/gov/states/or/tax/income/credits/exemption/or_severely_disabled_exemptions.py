from openfisca_us.model_api import *


class or_severely_disabled_exemptions(Variable):
    value_type = int
    entity = TaxUnit
    label = "OR severely disabled exemptions for tax head or spouse"
    definition_period = YEAR
    reference = (
        "https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=17"
        "https://www.oregonlegislature.gov/bills_laws/ors/ors316.html"  # Subsection 316.758(1)(b)
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        # Identify qualifying tax unit members.
        person = tax_unit.members
        severely_disabled = person("is_severely_disabled", period)
        head_or_spouse = ~person("is_tax_unit_dependent", period)
        # Determine eligibility from AGI.
        federal_agi = tax_unit("adjusted_gross_income", period)
        p = parameters(period).gov.states["or"].tax.income.credits.exemption
        qualifies = federal_agi <= p.income_limit.severely_disabled
        return qualifies * tax_unit.sum(severely_disabled & head_or_spouse)
