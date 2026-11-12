from policyengine_us.model_api import *
from policyengine_us.tools.mt_separate_return import (
    mt_medical_deduction,
    mt_medical_floor_room,
    mt_separate_tax_before_refundable_credits,
)

# Two allocations whose taxes differ by no more than this are treated as equal,
# so float32 noise does not decide between them.
TAX_TOLERANCE = 0.01


class mt_dependent_medical_expense_head_share(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Montana head's share of dependents' medical expenses when married couples file separately on the same form"
    unit = "/1"
    documentation = (
        "The share of the dependents' other medical expenses (Itemized "
        "Deductions Schedule line 1a) placed in the head's column when spouses "
        "file separately on the same form; the spouse's column takes the "
        "rest. For bills paid from accounts both spouses own, the form lets "
        "the couple divide them in any proportion, so the model picks the "
        "share that gives the lowest combined tax before refundable credits "
        "(Form 2 line 20 in both columns), holding every other itemized "
        "deduction fixed. It compares the equal split "
        "(spouse_allocation_rate), all to the head, all to the spouse, and "
        "the share at which the two columns' incomes before the dependent "
        "exemptions are equal, and the shares where each column exhausts "
        "its capital gain credit. While both columns are above their 7.5% "
        "floors, the total deduction does not depend on the share. Without "
        "binding credits, the couple's tax is convex in the share and "
        "lowest where the columns balance. "
        "Where a column is below its floor, bills moved into it are wasted "
        "and the tax is monotone in the share, so the shares at which a "
        "floor starts to bind never beat all to one spouse. A column's "
        "capital gain credit can move the minimum away from balance to "
        "the point where the column exhausts its credit. Ties go to the share closest to the "
        "equal split. The comparisons allow numerical tolerance. "
        "The tax is evaluated in closed form with the column "
        "variables' own formulas (policyengine_us.tools.mt_separate_return), "
        "not with simulation branches. Unmarried filers and couples without "
        "dependents' expenses get the equal split, which has no effect."
    )
    reference = (
        # PDF pages 11, 32-33, 43: deduction allocation, line 1, capital gain credit.
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=11",
        # ARM 42.15.524(3)(b): on the same form, a deduction not clearly
        # attributable to one spouse "may be divided as provided on the form".
        "https://web.archive.org/web/20201030190413/http://www.mtrules.org/gateway/ruleno.asp?RN=42.15.524",
    )
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income
        equal_split = p.deductions.itemized.spouse_allocation_rate
        default = np.full(tax_unit.count, equal_split, dtype=float)
        if not p.married_filing_separately_on_same_return_allowed:
            return default
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        head_or_spouse = head | spouse
        expense = person("other_medical_expenses", period)
        pool = tax_unit.sum(expense * ~head_or_spouse)
        own_expense = head_or_spouse * expense
        other_itemized = person("mt_non_medical_itemized_deductions_indiv", period)

        def couple_tax(head_share):
            share = tax_unit.project(head_share)
            column_share = where(head, share, where(spouse, 1 - share, 0))
            line_1a = own_expense + column_share * tax_unit.project(pool)
            itemized = other_itemized + mt_medical_deduction(
                person, period, parameters, line_1a
            )
            return mt_separate_tax_before_refundable_credits(
                tax_unit, period, parameters, itemized
            )

        # The share at which the two columns' incomes before the dependent
        # exemptions are equal. While both columns are above their 7.5%
        # floors, each extra dollar of bills is deductible in either column,
        # so the total deduction is fixed. Without binding credits, the
        # couple's tax is convex in the share, lowest where columns balance.
        # There a column's
        # income is level - share x pool, where level is its income with line
        # 1a at its floor (room is how far line 1a is below the floor); the
        # spouse's uses 1 - share. Where a column is below its floor, bills
        # moved into it are wasted, so the tax is monotone there and the
        # shares at which a floor starts to bind never beat 0 or 1.
        room = mt_medical_floor_room(person, period, parameters)
        safe_pool = where(pool > 0, pool, 1)
        kink_deduction = mt_medical_deduction(
            person, period, parameters, own_expense + room
        )
        level = (
            person("mt_agi_indiv", period)
            - person("mt_personal_exemptions_indiv", period)
            - other_itemized
            - kink_deduction
            + room
        )
        gap = tax_unit.sum(level * head) - tax_unit.sum(level * spouse)
        balance = np.clip(0.5 + gap / (2 * safe_pool), 0, 1)
        candidates = [
            (np.full(tax_unit.count, 0.0), True),
            (np.full(tax_unit.count, 1.0), True),
            (balance, True),
        ]
        if not p.main.capital_gains.in_effect:
            # A credit can hold the higher column's tax at zero. Add the
            # shares where each column exhausts its credit.
            schedule = p.main.separate
            thresholds = np.asarray(schedule.thresholds, dtype=float)
            tax_at_thresholds = schedule.calc(thresholds)
            credits = person("mt_non_refundable_credits", period)
            credit_income = np.interp(credits, tax_at_thresholds, thresholds)
            credit_income += (
                max_(credits - tax_at_thresholds[-1], 0) / schedule.rates[-1]
            )
            dependent_exemptions = tax_unit.sum(
                person("mt_dependent_exemptions_person", period)
            )
            balanced_income = max_(
                (tax_unit.sum(level * head_or_spouse) - pool - dependent_exemptions)
                / 2,
                0,
            )
            # Dependent exemptions first reduce the higher column. A credit
            # threshold above balanced taxable income needs the full
            # dependent exemption added back.
            required_income = credit_income + where(
                credit_income > tax_unit.project(balanced_income),
                tax_unit.project(dependent_exemptions),
                0,
            )
            for column, is_head in [(head, True), (spouse, False)]:
                allocation = (
                    tax_unit.sum((level - required_income) * column) / safe_pool
                )
                candidate = np.clip(allocation if is_head else 1 - allocation, 0, 1)
                # Ignore zero credits to preserve the existing candidates
                # when neither spouse receives a credit.
                has_credit = tax_unit.sum(credits * column) > 0
                candidates.append((candidate, has_credit))
        best_share = default
        best_tax = couple_tax(default)
        for candidate, eligible in candidates:
            tax = couple_tax(candidate)
            lower = tax < best_tax - TAX_TOLERANCE
            tied_and_closer = (np.abs(tax - best_tax) <= TAX_TOLERANCE) & (
                np.abs(candidate - equal_split) < np.abs(best_share - equal_split)
            )
            take = eligible & (lower | tied_and_closer)
            best_share = where(take, candidate, best_share)
            best_tax = where(take, tax, best_tax)
        married = tax_unit("tax_unit_married", period)
        return where(married & (pool > 0), best_share, default)
