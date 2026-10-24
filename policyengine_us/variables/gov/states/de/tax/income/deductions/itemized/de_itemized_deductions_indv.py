from policyengine_us.model_api import *


# The person-level expenses each itemized deduction is built from. A deduction
# is allocated to the spouse who paid the expense; amounts paid by dependents,
# and any deduction not listed here, cannot be specifically allocated to a
# spouse and are prorated by income.
EXPENSE_SOURCES = {
    "de_capped_real_estate_tax": ["real_estate_taxes"],
    "charitable_deduction": ["total_charitable_donations"],
    "interest_deduction": ["deductible_interest_expense"],
    "casualty_loss_deduction": ["casualty_loss"],
}


def _share(numerator, denominator):
    # numerator / denominator, or 0 where the denominator is not positive.
    share = np.zeros_like(denominator)
    mask = denominator > 0
    share[mask] = numerator[mask] / denominator[mask]
    return share


class de_itemized_deductions_indv(Variable):
    value_type = float
    entity = Person
    label = "Delaware itemized deductions when married couples are filing separately"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.delaware.gov/2022/TY22_PIT-RSA_2022-02_PaperInteractive.pdf",  # § 1109
        "https://delcode.delaware.gov/title30/c011/sc02/index.html",
        # 2023 PIT-RES instructions, line 13: prorate only the deductions that
        # cannot be specifically allocated between spouses.
        "https://revenuefiles.delaware.gov/2023/PIT-RES_TY23_2023-01_Instructions.pdf#page=7",
        # 2021 PIT-RES instructions, PDF pages 7, 12: specific allocation
        # where possible; PIT-RSA line 8d includes qualified premiums.
        "https://revenuefiles.delaware.gov/2021/PIT-RES_TY21_2021-01_Instructions.pdf#page=7",
    )
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        p = parameters(period).gov.states.de.tax.income.deductions.itemized
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # Proration for deductions that cannot be specifically allocated: each
        # spouse's share of the couple's separate income, counting only
        # positive income so that no spouse gets a negative deduction. With no
        # positive income, the spouses split the deduction equally.
        income = head_or_spouse * max_(
            person("adjusted_gross_income_person", period), 0
        )
        total_income = person.tax_unit.sum(income)
        filers = person.tax_unit.sum(head_or_spouse)
        income_share = where(
            total_income > 0,
            _share(income, total_income),
            _share(head_or_spouse * 1.0, filers * 1.0),
        )
        # Allocate each deduction to the spouse who paid the underlying expense.
        allocated = person.empty_array()
        for deduction in p.sources:
            expense_sources = EXPENSE_SOURCES.get(deduction)
            if expense_sources is None:
                continue
            amount = person.tax_unit(deduction, period)
            if deduction == "interest_deduction":
                premiums = person.tax_unit(
                    "deductible_mortgage_insurance_premiums", period
                )
                premium_expense = add(
                    person,
                    period,
                    [
                        "mortgage_insurance_premiums",
                        "second_residence_mortgage_insurance_premiums",
                    ],
                )
                total_premium_expense = person.tax_unit.sum(premium_expense)
                filer_premium_expense = person.tax_unit.sum(
                    head_or_spouse * premium_expense
                )
                # Allocate the post-phase-out premium component separately.
                # The federal person allocation conserves the entire amount
                # across filers; retain only the known-payer share here so
                # dependent/unknown expenses use Delaware's income fallback.
                allocated += person(
                    "deductible_mortgage_insurance_premiums_indiv", period
                ) * _share(filer_premium_expense, total_premium_expense)
                amount = max_(amount - premiums, 0)
            expense = add(person, period, expense_sources)
            total_expense = person.tax_unit.sum(expense)
            allocated += amount * _share(head_or_spouse * expense, total_expense)
        # Prorate what could not be specifically allocated.
        unit_deductions = person.tax_unit("de_itemized_deductions_unit", period)
        # An aggregate override can be below the traced deductions; never
        # subtract a negative remainder from either spouse's allocation.
        unallocated = max_(unit_deductions - person.tax_unit.sum(allocated), 0)
        return allocated + unallocated * income_share
