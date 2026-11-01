from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.income.dependent_gross_income import (
    DEPENDENT_GROSS_INCOME_SOURCE_OVERRIDES,
)

# Gross income sources whose losses loss_ald deducts from gross income.
BUSINESS_LOSS_SOURCES = [
    "self_employment_income",
    "sstb_self_employment_income",
    "partnership_s_corp_income",
    "farm_operations_income",
    "farm_rent_income",
    "rental_income",
]

# Above-the-line deductions the model can attribute to one person, keyed by
# their name in gov.irs.ald.deductions.
PERSON_ABOVE_THE_LINE_DEDUCTIONS = {
    "self_employment_tax_ald": "self_employment_tax_ald_person",
    "self_employed_health_insurance_ald": "self_employed_health_insurance_ald_person",
    "self_employed_pension_contribution_ald": "self_employed_pension_contribution_ald_person",
    "educator_expense_ald": "educator_expense_ald_person",
    "early_withdrawal_penalty": "early_withdrawal_penalty",
    # The dependent's own IRC 219 deduction, figured on their own return; the
    # filer's traditional_ira_deduction is limited to the head and spouse.
    "traditional_ira_deduction": "dependent_traditional_ira_deduction",
    "alimony_expense_ald": "alimony_expense_ald_person",
}


def dependent_income_and_deductions(person, period, parameters):
    """A dependent's own-return income before above-the-line deductions, and
    the person-level above-the-line deductions to subtract from it.

    Income nets business losses and capital losses (within the IRC 1211(b)
    limit) and leaves out Social Security, as IRC 86(b)(2) requires.
    """
    p = parameters(period).gov.irs
    sources = p.gross_income.sources
    revoked = p.social_security.taxability.income.revoked_deductions
    ald = [deduction for deduction in p.ald.deductions if deduction not in revoked]
    deduct_losses = "loss_ald" in ald

    # Capital gain distributions net with capital gains and losses on
    # Schedule D (line 13), inside the IRC 1211(b) limit, below.
    net_distributions = (
        "capital_gains" in sources and "non_sch_d_capital_gains" in sources
    )

    income = 0
    for source in sources:
        components = DEPENDENT_GROSS_INCOME_SOURCE_OVERRIDES.get(source, [source])
        for component in components:
            if net_distributions and component == "non_sch_d_capital_gains":
                continue
            amount = add(person, period, [component])
            if deduct_losses and component in BUSINESS_LOSS_SOURCES:
                income += amount
            else:
                income += max_(0, amount)

    if "capital_gains" in sources:
        # IRC 1211(b): net capital losses are deductible up to the limit,
        # which is lower for a married individual filing separately.
        lives_with_spouse = person("dependent_lives_with_spouse", period)
        capital_loss_limit = p.ald.loss.capital.max
        loss_limit = deduct_losses * where(
            lives_with_spouse,
            capital_loss_limit["SEPARATE"],
            capital_loss_limit["SINGLE"],
        )
        capital_gains = person("capital_gains", period)
        if net_distributions:
            capital_gains = capital_gains + max_(
                0, person("non_sch_d_capital_gains", period)
            )
        income += max_(capital_gains, -loss_limit)

    deductions = [
        PERSON_ABOVE_THE_LINE_DEDUCTIONS[deduction]
        for deduction in ald
        if deduction in PERSON_ABOVE_THE_LINE_DEDUCTIONS
    ]
    return income, deductions


class dependent_taxable_ss_magi(Variable):
    value_type = float
    entity = Person
    label = "Dependent's modified adjusted gross income for Social Security taxability"
    unit = USD
    documentation = """
    The modified adjusted gross income of IRC 86(b)(2), figured on a
    dependent's own return: adjusted gross income without taxable Social
    Security, without the exclusions and deductions of IRC 85(c), 135, 137,
    221, 911, 931 and 933, plus tax-exempt interest. Unlike the qualifying
    relative gross income test, losses and above-the-line deductions reduce
    it. Above-the-line deductions the model records only for the tax unit
    (health savings account contributions) are not attributed to
    dependents, and the IRC 461(l) excess business loss limit is not
    applied.
    """
    definition_period = YEAR
    defined_for = "is_tax_unit_dependent"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/86#b_2",
        "https://www.law.cornell.edu/uscode/text/26/62#a",
        "https://www.law.cornell.edu/uscode/text/26/1211#b",
        # IRS Pub. 915 (2022), Worksheet 1, lines 3 through 8.
        "https://www.irs.gov/pub/irs-prior/p915--2022.pdf#page=16",
    )

    def formula(person, period, parameters):
        income, deductions = dependent_income_and_deductions(person, period, parameters)
        adjusted_gross_income = income - add(person, period, deductions)
        # IRC 86(b)(2)(B): tax-exempt interest is added back.
        return adjusted_gross_income + person("tax_exempt_interest_income", period)
