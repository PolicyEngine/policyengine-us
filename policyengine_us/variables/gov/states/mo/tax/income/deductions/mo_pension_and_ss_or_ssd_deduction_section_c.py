from policyengine_us.model_api import *


class mo_pension_and_ss_or_ssd_deduction_section_c(Variable):
    value_type = float
    entity = Person
    label = "MO Pension and Social Security or SS Disability Deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-A_2021.pdf#page=3",
        "https://dor.mo.gov/forms/MO-1040%20Fillable%20Calculating_2021.pdf#page=2",
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.124",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        mo_agi = person("mo_adjusted_gross_income", period)
        tax_unit_mo_agi = tax_unit.sum(mo_agi)

        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.mo.tax.income.deductions
        ss_or_ssd_agi_allowance = p.mo_ss_or_ssd_deduction_allowance[
            filing_status
        ]
        agi_over_ss_or_ssd_allowance = max_(
            tax_unit_mo_agi - ss_or_ssd_agi_allowance, 0
        )  # different from Sections A and B, Line 3, floor at 0.
        tax_unit_taxable_social_security_benefits = add(
            tax_unit, period, ["taxable_social_security"]
        )

        return max_(
            tax_unit_taxable_social_security_benefits
            - agi_over_ss_or_ssd_allowance,
            0,
        )
