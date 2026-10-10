from policyengine_us.model_api import *


class az_increased_excise_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Eligible for Arizona Increased Excise Tax Credit"
    reference = (
        "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01072-01.htm",
        # Form 140 line 56 instructions.
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_140i.pdf#page=25",
    )
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.credits.increased_excise
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        max_income = p.income_threshold[filing_status]
        # A.R.S. 43-1072.01(A) allows the credit only "for a taxpayer who is
        # not claimed as a dependent by any other taxpayer". On a joint
        # return a spouse who is not claimed can still claim it.
        every_filer_is_dependent = tax_unit(
            "every_filer_is_dependent_elsewhere", period
        )
        return (agi <= max_income) & ~every_filer_is_dependent
