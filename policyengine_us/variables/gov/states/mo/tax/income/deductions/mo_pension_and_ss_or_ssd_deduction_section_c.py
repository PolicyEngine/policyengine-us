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
        ind_mo_agi = person("mo_adjusted_gross_income", period)
        unit_mo_agi = tax_unit.sum(ind_mo_agi)
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.mo.tax.income.deductions
        unit_allowance = p.mo_ss_or_ssd_deduction_allowance[filing_status]
        unit_agi_over_allowance = max_(0, unit_mo_agi - unit_allowance)
        ind_taxable_ben = person("taxable_social_security", period)
        unit_taxable_ben = tax_unit.sum(ind_taxable_ben)
        unit_deduction = max_(0, unit_taxable_ben - unit_agi_over_allowance)
        # Compute the individual's share of the tax unit's taxable benefits.
        # Use a mask rather than where to avoid a divide-by-zero warning. Default to zero.
        ind_frac = np.zeros_like(ind_taxable_ben)
        mask = ind_taxable_ben > 0
        ind_frac[mask] = ind_taxable_ben[mask] / unit_taxable_ben[mask]
        return ind_frac * unit_deduction
