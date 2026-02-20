from policyengine_us.model_api import *


class mo_pension_and_ss_or_ssd_deduction_section_c(Variable):
    value_type = float
    entity = Person
    label = "Missouri Social Security or SS Disability Deduction (Section C)"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-A_2024.pdf#page=3",
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.124",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.mo.tax.income.deductions.social_security_and_public_pension

        # Per MO-A 2024 Section C: SS deduction requires age 62+ by Dec 31;
        # SSDI has no age limit.
        age = person("age", period)
        age_threshold = p.age_threshold
        meets_age_requirement = age >= age_threshold

        # Get taxable social security (allocated from tax unit calculation)
        ind_taxable_ss = person("taxable_social_security", period)

        # Calculate the SSDI portion of taxable SS for those under age threshold.
        # SSDI has no age limit, so we need to determine what portion of
        # taxable SS is attributable to SSDI.
        ind_ssdi = person("social_security_disability", period)
        ind_total_ss = person("social_security", period)

        # Compute SSDI fraction of total SS (avoid divide by zero)
        ssdi_fraction = np.zeros_like(ind_total_ss)
        mask = ind_total_ss > 0
        ssdi_fraction[mask] = ind_ssdi[mask] / ind_total_ss[mask]

        # Taxable SSDI is the SSDI fraction of taxable SS
        ind_taxable_ssdi = ind_taxable_ss * ssdi_fraction

        # For age 62+: full taxable SS is deductible
        # For under 62: only taxable SSDI portion is deductible
        eligible_taxable_benefits = where(
            meets_age_requirement, ind_taxable_ss, ind_taxable_ssdi
        )

        if p.income_threshold_applies:
            # Pre-2024: Apply income-based phase-out
            tax_unit = person.tax_unit
            ind_mo_agi = person("mo_adjusted_gross_income", period)
            unit_mo_agi = tax_unit.sum(ind_mo_agi)
            filing_status = tax_unit("filing_status", period)
            unit_allowance = p.mo_ss_or_ssd_deduction_allowance[filing_status]
            unit_agi_over_allowance = max_(0, unit_mo_agi - unit_allowance)
            unit_eligible_ben = tax_unit.sum(eligible_taxable_benefits)
            unit_deduction = max_(
                0, unit_eligible_ben - unit_agi_over_allowance
            )
            # Compute individual's share of tax unit deduction
            ind_frac = np.zeros_like(eligible_taxable_benefits)
            ben_mask = eligible_taxable_benefits > 0
            ind_frac[ben_mask] = (
                eligible_taxable_benefits[ben_mask]
                / unit_eligible_ben[ben_mask]
            )
            return ind_frac * unit_deduction

        # 2024+: No income threshold, full eligible benefits are deductible
        return eligible_taxable_benefits
