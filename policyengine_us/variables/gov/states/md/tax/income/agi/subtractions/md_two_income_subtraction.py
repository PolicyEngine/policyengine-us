from policyengine_us.model_api import *


# Person-level sources of the business losses in loss_ald.
BUSINESS_LOSS_SOURCES = [
    "total_self_employment_income",
    "farm_operations_income",
    "rental_income",
    "farm_rent_income",
    "estate_income",
    "partnership_s_corp_income",
]


def _head_part(amount, head_own, spouse_own):
    """The head's part of an amount split by the spouses' own amounts, or
    equally when neither has any."""
    total = head_own + spouse_own
    frac = np.full_like(total, 0.5)
    mask = total > 0
    frac[mask] = head_own[mask] / total[mask]
    return amount * frac


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
        # Compute the head's share of the couple's gross income.
        # Use a mask rather than where to avoid a divide-by-zero warning.
        head_frac = np.ones_like(couple_gross_income)
        mask = couple_gross_income > 0
        head_frac[mask] = head_gross_income[mask] / couple_gross_income[mask]
        # Gross income is never below zero (losses are deducted in loss_ald),
        # so without gross income the couple's AGI is their allowed losses and
        # above-the-line deductions, and each spouse's portion is the part
        # that is their own. The allowed business and capital losses in
        # loss_ald are each split by the spouses' own losses of that kind,
        # and deductions go to their owner where a person-level amount
        # records one. Whatever has no owner is split equally.
        filer = is_head | is_spouse
        own_business = 0
        for source in BUSINESS_LOSS_SOURCES:
            own_business = own_business + max_(0, -person(source, period))
        own_business = filer * own_business
        unit_business = max_(0, -tax_unit("other_net_gain", period)) / 2
        own_capital = filer * person("capital_losses", period)
        capital_part = add(
            tax_unit,
            period,
            ["limited_capital_loss", "capital_losses_allowed_against_gains"],
        )
        loss_ald = tax_unit("loss_ald", period)
        business_part = max_(0, loss_ald - capital_part)
        head_loss = _head_part(
            business_part,
            tax_unit.sum(is_head * own_business) + unit_business,
            tax_unit.sum(is_spouse * own_business) + unit_business,
        ) + _head_part(
            capital_part,
            tax_unit.sum(is_head * own_capital),
            tax_unit.sum(is_spouse * own_capital),
        )
        spouse_loss = loss_ald - head_loss
        # A tax-unit deduction with a person-level counterpart is split by
        # the spouses' own amounts, or equally when neither has one.
        head_deductions = 0
        spouse_deductions = 0
        for deduction in sorted(parameters(period).gov.irs.ald.deductions):
            variable = person.entity.get_variable(deduction, check_existence=True)
            if variable.entity.is_person:
                amount = filer * person(deduction, period)
                head_deductions = head_deductions + tax_unit.sum(is_head * amount)
                spouse_deductions = spouse_deductions + tax_unit.sum(is_spouse * amount)
                continue
            counterpart = f"{deduction}_person"
            if person.entity.get_variable(counterpart) is None:
                continue
            own = filer * person(counterpart, period)
            unit_amount = tax_unit(deduction, period)
            head_part = _head_part(
                unit_amount, tax_unit.sum(is_head * own), tax_unit.sum(is_spouse * own)
            )
            head_deductions = head_deductions + head_part
            spouse_deductions = spouse_deductions + unit_amount - head_part
        head_own = -head_loss - head_deductions
        spouse_own = -spouse_loss - spouse_deductions
        unattributed = us_agi - head_own - spouse_own
        no_gross_income = couple_gross_income <= 0
        head_us_agi = where(
            no_gross_income, head_own + unattributed / 2, head_frac * us_agi
        )
        spouse_us_agi = where(
            no_gross_income, spouse_own + unattributed / 2, (1 - head_frac) * us_agi
        )

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
