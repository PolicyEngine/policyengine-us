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
        # calculate tax unit MO AGI
        tax_unit = person.tax_unit
        mo_agi = person("mo_adjusted_gross_income", period)
        unit_mo_agi = tax_unit.sum(mo_agi)

        # calculate sum of all tax unit MO deductions
        mo_itemized_or_standard = where(
            tax_unit("tax_unit_itemizes", period),  # itemizes on federal form
            tax_unit("mo_itemized_deductions", period),
            tax_unit("standard_deduction", period),  # equal to federal stdded
        )
        mo_federal_income_tax_deduction = tax_unit(
            "mo_federal_income_tax_deduction", period
        )
        mo_pension_and_ss_or_ssd_deduction = tax_unit(
            "mo_pension_and_ss_or_ssd_deduction", period
        )
        unit_mo_deductions = (
            mo_itemized_or_standard
            + mo_federal_income_tax_deduction  # available to all tax units
            + mo_pension_and_ss_or_ssd_deduction  # available to all tax units
        )
        # Note: There would also be a personal and/or dependent exemptions
        # as part of this formula, but they are legally based on eligibility
        # for the federal versions of those exemptions, both of which are
        # suspended through 2025 federally.

        # calculate taxable income for tax unit
        unit_taxinc = max_(0, unit_mo_agi - unit_mo_deductions)

        # Allocate tax unit taxable income by each individual's share of unit AGI.
        # Use a mask rather than where to avoid a divide-by-zero warning. Default to zero.
        ind_agi_share = np.zeros_like(unit_mo_agi)
        mask = unit_mo_agi > 0
        ind_agi_share[mask] = mo_agi[mask] / unit_mo_agi[mask]

        return ind_agi_share * unit_taxinc
