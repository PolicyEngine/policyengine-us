from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.tax_unit.filing_status import (
    FilingStatus,
)

# The wage and self-employment sources in gov.irs.gross_income.sources.
EARNED_GROSS_INCOME_SOURCES = [
    "irs_employment_income",
    "self_employment_income",
    "sstb_self_employment_income",
]


class medicaid_person_is_required_to_file(Variable):
    value_type = bool
    entity = Person
    label = "Person is required to file for Medicaid MAGI child/dependent income rules"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.603#d_2",
        "https://www.irs.gov/publications/p501",
        "https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=4",
    )

    def formula(person, period, parameters):
        standard = parameters(period).gov.irs.deductions.standard
        filing_requirement = parameters(period).gov.irs.income.filing_requirement
        gross_income = person("medicaid_irs_gross_income", period)
        earned_income = person("earned_income", period)
        # Unearned income is gross income other than wages and self-employment
        # earnings (IRS Pub. 501, Table 2). Gross income counts each source's
        # positive amount, so subtract those sources' positive amounts: a
        # business loss does not turn other income into unearned income.
        earned_gross_income = 0
        for source in EARNED_GROSS_INCOME_SOURCES:
            earned_gross_income += max_(0, person(source, period))
        unearned_income = max_(0, gross_income - earned_gross_income)

        married = person.marital_unit.nb_persons() == 2
        filing_status = where(married, FilingStatus.SEPARATE, FilingStatus.SINGLE)
        aged_or_blind_count = (
            person("age", period.this_year) >= standard.aged_or_blind.age_threshold
        ).astype(int) + person("is_blind", period).astype(int)
        additional_deduction = (
            standard.aged_or_blind.amount[filing_status] * aged_or_blind_count
        )
        regular_standard_deduction = standard.amount[filing_status]
        dependent_standard_deduction = (
            min_(
                regular_standard_deduction,
                max_(
                    standard.dependent.amount,
                    standard.dependent.additional_earned_income + earned_income,
                ),
            )
            + additional_deduction
        )
        spouse_itemizes = married & person.tax_unit("separate_filer_itemizes", period)

        return (
            (
                spouse_itemizes
                & (
                    gross_income
                    >= filing_requirement.dependent.spouse_itemizes_threshold
                )
            )
            | (unearned_income > (standard.dependent.amount + additional_deduction))
            | (earned_income > (regular_standard_deduction + additional_deduction))
            | (gross_income > dependent_standard_deduction)
        )
