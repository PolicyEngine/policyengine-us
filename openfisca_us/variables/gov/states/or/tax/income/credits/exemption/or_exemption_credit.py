from openfisca_us.model_api import *


class or_exemption_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR exemption credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=17"
        "https://www.oregonlegislature.gov/bills_laws/ors/ors316.html"  # Subsection 316.085
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        EXEMPTION_TYPES = [
            "regular",
            "severely_disabled",
            "disabled_child_dependent",
        ]
        exemptions = add(
            tax_unit,
            period,
            ["or_" + i + "_exemptions" for i in EXEMPTION_TYPES],
        )
        amount = (
            parameters(period)
            .gov.states["or"]
            .tax.income.credits.exemption.amount
        )
        return exemptions * amount
