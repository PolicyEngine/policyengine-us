from policyengine_us.model_api import *


class vt_capital_gain_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont capital gain exclusion"
    unit = USD
    documentation = "This is subtracted from federal adjusted gross income in Vermont as captial gain exclusion."
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112-2022.pdf#page=1"  # PART 1 SUBTRACTIONS TO FEDERAL ADJUSTED GROSS INCOME
        "https://legislature.vermont.gov/statutes/section/32/151/05811"  # Titl. 32 V.S.A. § 5811(21)(B)(ii)
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112%20Instr-2022.pdf"
    )

    def formula(tax_unit, period, parameters):
        capital_gains_excluded_from_taxable_income = tax_unit(
            "capital_gains_excluded_from_taxable_income", period
        )
        p = parameters(
            period
        ).gov.states.vt.tax.income.agi.capital_gain_exclusion
        # The exclusion amount have a maximum value
        return min_(capital_gains_excluded_from_taxable_income, p.max)
