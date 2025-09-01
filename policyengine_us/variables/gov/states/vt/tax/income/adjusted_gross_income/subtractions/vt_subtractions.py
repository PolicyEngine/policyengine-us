from policyengine_us.model_api import *


class vt_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont subtractions"
    unit = USD
    documentation = "Subtractions from Vermont adjusted gross income"
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112-2022.pdf#page=1",  # PART 1 SUBTRACTIONS TO FEDERAL ADJUSTED GROSS INCOME
        "https://legislature.vermont.gov/statutes/section/32/151/05811",  # Titl. 32 V.S.A. § 5811(21)(B)(i), (C)(iv), (B)(vi), (B)(ii), (B)(iv)
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112%20Instr-2022.pdf",
    )

    # Get parameter list
    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.agi
        total_subtractions = add(tax_unit, period, p.subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
