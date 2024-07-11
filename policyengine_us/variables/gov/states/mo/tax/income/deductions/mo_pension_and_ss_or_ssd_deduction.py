from policyengine_us.model_api import *


class mo_pension_and_ss_or_ssd_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri Pension and Social Security or SS Disability Deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-A_2021.pdf#page=3",
        "https://dor.mo.gov/forms/MO-1040%20Fillable%20Calculating_2021.pdf#page=2",
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.124",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # Section C, SS or SSD Amounts
        # We start with section C because, in situations where someone receives both a pension and taxable
        # Social Security, Section A requires information from Section C to be completed.
        eligible_ss_or_ssd = person(
            "mo_pension_and_ss_or_ssd_deduction_section_c", period
        )
        tax_unit_eligible_ss_or_ssd = tax_unit.sum(eligible_ss_or_ssd)
        # Section A, Public Pension Amounts
        # TODO:
        # unclear reference to "See instructions if Line 3 of Section C is more than $0" here: https://dor.mo.gov/forms/MO-A_2021.pdf#page=3
        public_pensions = person(
            "mo_pension_and_ss_or_ssd_deduction_section_a", period
        )
        tax_unit_eligible_total_public_pensions = tax_unit.sum(public_pensions)
        # Section B, Private Pension Amounts
        total_private_pensions = person(
            "mo_pension_and_ss_or_ssd_deduction_section_b", period
        )
        tax_unit_total_private_pensions = tax_unit.sum(total_private_pensions)
        return (
            tax_unit_total_private_pensions
            + tax_unit_eligible_total_public_pensions
            + tax_unit_eligible_ss_or_ssd
        )
