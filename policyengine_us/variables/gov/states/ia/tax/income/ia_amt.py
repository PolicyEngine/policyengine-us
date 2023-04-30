from policyengine_us.model_api import *


class ia_amt(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa alternative minimum tax"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2021-12/IA6251%2841131%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/IA6251%2841131%29.pdf"
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        # compute Iowa AMT taxable income
        reg_taxinc = tax_unit("ia_taxable_income", period)
        std_ded = tax_unit("ia_standard_deduction", period)
        itm_ded = tax_unit("ia_itemized_deductions", period)
        amt_taxinc = where(
            itm_ded > std_ded,
            reg_taxinc + add(tax_unit, period, ["real_estate_taxes"]),
            reg_taxinc,
        )
        # compute AMT amount
        p = parameters(period).gov.states.ia.tax.income
        amt = p.alternative_minimum_tax
        filing_status = tax_unit("filing_status", period)
        amt_threshold = amt.threshold[filing_status]  # Line 23
        amt_exemption = amt.exemption[filing_status]  # Line 24
        netinc = max_(0, amt_taxinc - amt_exemption)  # Line 25
        amount = max_(0, amt_threshold - netinc * amt.fraction)  # Line 27
        gross_amt = max_(0, amt_taxinc - amount) * amt.rate  # Line 29
        basic_tax = tax_unit("ia_basic_tax", period)  # Line 30
        return max_(0, gross_amt - basic_tax)  # Line 31
