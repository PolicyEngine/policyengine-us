from policyengine_us.model_api import *


class md_two_income_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD two-income married couple subtraction from AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=16"
        "https://govt.westlaw.com/mdc/Document/NF93A7BD2E6C811ECA065A3F5EAA0E5C9?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)"
    )
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        is_joint = filing_status == filing_status.possible_values.JOINT
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
        # Compute the head's share of the couple's cross income.
        # Use a mask rather than where to avoid a divide-by-zero warning. Default to one.
        head_frac = np.ones_like(couple_gross_income)
        mask = couple_gross_income > 0
        head_frac[mask] = head_gross_income[mask] / couple_gross_income[mask]
        head_us_agi = head_frac * us_agi
        spouse_us_agi = (1 - head_frac) * us_agi

        # compute head and spouse MD AGI additions using ad hoc rule
        total_additions = tax_unit("md_total_additions", period)
        head_adds = 0.5 * total_additions
        spouse_adds = 0.5 * total_additions

        # sum head and spouse MD AGI subtractions (other than two-income)
        head_subs = 0
        spouse_subs = 0
        p = parameters(period).gov.states.md.tax.income.agi.subtractions
        for sub in p.sources:
            if sub == "md_two_income_subtraction":
                continue
            if sub in ["md_pension_subtraction", "md_socsec_subtraction"]:
                # person-level subtractions
                ind_sub = person(sub + "_amount", period)
                head_subs += tax_unit.sum(is_head * ind_sub)
                spouse_subs += tax_unit.sum(is_spouse * ind_sub)
            else:
                # taxunit-level subtractions
                unit_sub = tax_unit(sub, period)
                head_subs += 0.5 * unit_sub
                spouse_subs += 0.5 * unit_sub

        # compute MD two-income subtraction
        min_agi_adds_subs = min_(
            head_us_agi + head_adds - head_subs,
            spouse_us_agi + spouse_adds - spouse_subs,
        )
        capped_min_agi_adds_subs = min_(
            p.max_two_income_subtraction,
            min_agi_adds_subs,
        )
        return is_joint * max_(0, capped_min_agi_adds_subs)
