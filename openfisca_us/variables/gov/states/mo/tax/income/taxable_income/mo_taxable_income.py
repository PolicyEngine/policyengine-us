from openfisca_us.model_api import *


class mo_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri AGI minus deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-A_2021.pdf",
        "https://www.revisor.mo.gov/main/OneSection.aspx?section=143.111&bid=7201&hl=",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        tax_unit_itemizes = tax_unit("tax_unit_itemizes", period)

        mo_agi = tax_unit("mo_adjusted_gross_income", period)
        mo_federal_income_tax_deduction = tax_unit(
            "mo_federal_income_tax_deduction", period
        )

        # MO standard deduction is set equal to the Federal standard deduction https://revisor.mo.gov/main/OneSection.aspx?section=143.131
        mo_standard_deduction = tax_unit("standard_deduction", period)
        mo_itemized_deductions = tax_unit("mo_itemized_deductions", period)
        mo_itemized_or_standard = where(
            tax_unit_itemizes, mo_itemized_deductions, mo_standard_deduction
        )
        # NB: The federal income tax deduction applies regardless of itemization.
        # Note: There would also be a personal and/or dependent exemptions as part of
        # this formula, but they are legally based on eligibility for the federal
        # versions of those exemptions, both of which are suspended through 2025 federally.
        return (
            mo_agi - mo_itemized_or_standard - mo_federal_income_tax_deduction
        )
