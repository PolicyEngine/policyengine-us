from policyengine_us.model_api import *


# Person-level sources of the business and capital losses in loss_ald.
LOSS_SOURCES = [
    "total_self_employment_income",
    "farm_operations_income",
    "rental_income",
    "farm_rent_income",
    "estate_income",
    "partnership_s_corp_income",
    "capital_gains",
]


class md_two_income_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD two-income married couple subtraction from AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://interactive.marylandtaxes.gov/Individuals/iFile_ChooseForm/PriorYearForms/Resident_Booklet_2021.pdf#page=16",
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-207&enactments=false",
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=18",
        # Worksheet 13D line 1: "the portion of federal adjusted gross income
        # from Line 1 of Form 502 attributable to each spouse"
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
        couple_gross_income = tax_unit.sum(where(is_head | is_spouse, gross_income, 0))
        # Without gross income, the couple's AGI is made up of losses and
        # above-the-line deductions, and each spouse's portion follows the
        # losses and deductions that are that spouse's own. Deductions
        # recorded only for the tax unit are split equally, as in
        # adjusted_gross_income_person. Use masks rather than where to avoid
        # divide-by-zero warnings.
        filer = is_head | is_spouse
        own_items = filer * sum(
            max_(0, -person(source, period)) for source in LOSS_SOURCES
        )
        for deduction in sorted(parameters(period).gov.irs.ald.deductions):
            if deduction == "loss_ald":
                continue
            variable = person.entity.get_variable(deduction, check_existence=True)
            if variable.entity.is_person:
                own_items = own_items + filer * person(deduction, period)
        couple_items = tax_unit.sum(own_items)
        head_frac = np.full_like(couple_gross_income, 0.5)
        has_items = couple_items > 0
        head_frac[has_items] = (
            tax_unit.sum(is_head * own_items)[has_items] / couple_items[has_items]
        )
        # With gross income, use the head's share of the couple's gross income.
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
