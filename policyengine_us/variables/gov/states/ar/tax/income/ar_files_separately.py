from policyengine_us.model_api import *


class ar_files_separately(Variable):
    value_type = bool
    entity = TaxUnit
    label = "married couple files separately on the Arkansas tax return"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_AR1000F_and_AR1000NR_Instructions.pdf"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf"
    )
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
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
        return itax_indiv < itax_joint
