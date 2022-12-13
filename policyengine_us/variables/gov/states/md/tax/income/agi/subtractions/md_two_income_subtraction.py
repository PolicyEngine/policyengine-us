from policyengine_us.model_api import *


class md_two_income_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD two-income married couple subtraction from AGI"
    unit = USD
    definition_period = YEAR
    reference = "https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=16"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # compute head and spouse US AGI portions using irs_gross_income shares
        us_agi = tax_unit("adjusted_gross_income", period)
        gross_income = person("irs_gross_income", period)
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        head_gross_income = tax_unit.sum(where(is_head, gross_income, 0))
        couple_gross_income = tax_unit.sum(
            where(is_head | is_spouse, gross_income, 0)
        )
        head_frac = where(
            couple_gross_income > 0, head_gross_income / couple_gross_income, 1
        )
        head_us_agi = head_frac * us_agi
        spouse_us_agi = (1 - head_frac) * us_agi

        # compute head and spouse MD AGI additions using ad hoc rule
        total_additions = tax_unit("md_total_additions", period)
        head_adds = 0.5 * total_additions
        spouse_adds = 0.5 * total_additions

        # compute head and spouse MD AGI subtractions
        p = parameters(period).gov.states.md.tax.income.agi.subtractions
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        head_subs = 0
        spouse_subs = 0
        for subtraction in p.sources:
            if subtraction == "md_two_income_subtraction":
                continue
            if subtraction == "md_dependent_care_subtraction":
                unit_care_amt = tax_unit(subtraction, period)
                head_frac = where(joint, 0.5, 1.0)
                head_subs += head_frac * unit_care_amt
                spouse_subs += (1 - head_frac) * unit_care_amt
            else:
                print("MD ERROR")

        # compute MD two-income subtraction
        min_agi_add_sub = min_(
            head_us_agi + head_adds - head_subs,
            spouse_us_agi + spouse_adds - spouse_subs,
        )
        capped_min_agi_add_sub = min_(
            p.max_two_income_subtraction,
            min_agi_add_sub,
        )
        return max_(0, capped_min_agi_add_sub)
