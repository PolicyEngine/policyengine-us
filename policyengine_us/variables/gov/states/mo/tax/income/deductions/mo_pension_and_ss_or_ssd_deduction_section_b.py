from policyengine_us.model_api import *


class mo_pension_and_ss_or_ssd_deduction_section_b(Variable):
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
        ind_mo_agi = person("mo_adjusted_gross_income", period)
        unit_mo_agi = tax_unit.sum(ind_mo_agi)
        ind_taxable_oasdi = person("taxable_social_security", period)
        unit_taxable_oasdi = tax_unit.sum(ind_taxable_oasdi)
        p = parameters(period).gov.states.mo.tax.income.deductions
        filing_status = tax_unit("filing_status", period)
        excess_agi = max_(  # line5
            0,
            (
                unit_mo_agi
                - unit_taxable_oasdi
                - p.mo_private_pension_deduction_allowance[filing_status]
            ),
        )
        ind_pvt_pen_amt = person("taxable_private_pension_income", period)
        ind_pvt_pen_val = min_(ind_pvt_pen_amt, p.mo_max_private_pension)
        unit_pvt_pen_val = tax_unit.sum(ind_pvt_pen_val)  # line8
        unit_deduction = max_(0, unit_pvt_pen_val - excess_agi)  # line9
        # Compute the individual's share of the tax unit's taxable private pension income.
        # Use a mask rather than where to avoid a divide-by-zero warning. Default to zero.
        ind_share = np.zeros_like(ind_pvt_pen_val)
        mask = ind_pvt_pen_val > 0
        ind_share[mask] = ind_pvt_pen_val[mask] / unit_pvt_pen_val[mask]

        return ind_share * unit_deduction
