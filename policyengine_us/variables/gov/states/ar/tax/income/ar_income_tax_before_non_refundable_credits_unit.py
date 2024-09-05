from policyengine_us.model_api import *


class ar_income_tax_before_non_refundable_credits_unit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas income tax before non refundable credits combined"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_AR1000F_and_AR1000NR_Instructions.pdf"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf"
    )
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        filing_separately = tax_unit("ar_files_separately", period)
        itax_indiv = add(
            tax_unit,
            period,
            ["ar_income_tax_before_non_refundable_credits_indiv"],
        )
        itax_joint = add(
            tax_unit,
            period,
            ["ar_income_tax_before_non_refundable_credits_joint"],
        )

        return where(filing_separately, itax_indiv, itax_joint)
