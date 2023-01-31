from policyengine_us.model_api import *


class mo_taxable_income(Variable):
    value_type = float
    entity = Person
    label = "Missouri AGI minus deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-A_2021.pdf",
        "https://www.revisor.mo.gov/main/OneSection.aspx?section=143.111&bid=7201&hl=",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        tax_unit_itemizes = tax_unit("tax_unit_itemizes", period)
        # Grab input variables.
        mo_agi = person("mo_adjusted_gross_income", period)
        tax_unit_mo_agi = tax_unit.sum(mo_agi)
        mo_federal_income_tax_deduction = tax_unit(
            "mo_federal_income_tax_deduction", period
        )
        # MO standard deduction is set equal to the Federal standard deduction https://revisor.mo.gov/main/OneSection.aspx?section=143.131
        mo_standard_deduction = tax_unit("standard_deduction", period)
        mo_itemized_deductions = tax_unit("mo_itemized_deductions", period)
        mo_itemized_or_standard = where(
            tax_unit_itemizes, mo_itemized_deductions, mo_standard_deduction
        )
        # MO Pension, Social Security, and Social Security Disability Exemption
        mo_pension_and_ss_or_ssd_deduction = tax_unit(
            "mo_pension_and_ss_or_ssd_deduction", period
        )

        # NB: The federal income tax deduction applies regardless of itemization.
        all_deductions_tax_unit = (
            mo_itemized_or_standard
            + mo_federal_income_tax_deduction
            + mo_pension_and_ss_or_ssd_deduction
        )
        # Note: There would also be a personal and/or dependent exemptions as part of
        # this formula, but they are legally based on eligibility for the federal
        # versions of those exemptions, both of which are suspended through 2025 federally.
        # Scale tax unit deductions by the person's share of tax unit AGI.
        # Apply where statement to avoid division by zero.
        person_share = where(tax_unit_mo_agi > 0, mo_agi / tax_unit_mo_agi, 0)
        all_deductions_person = person_share * all_deductions_tax_unit
        return max_(mo_agi - all_deductions_person, 0)
