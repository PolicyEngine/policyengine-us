from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.tax_unit.filing_status import (
    FilingStatus,
)


class medicaid_person_is_required_to_file(Variable):
    value_type = bool
    entity = Person
    label = "Person is required to file for Medicaid MAGI child/dependent income rules"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.603#d_2",
        "https://www.irs.gov/publications/p501",
        "https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=4",
        # Form 1040 instructions: line 1a is Form(s) W-2, box 1 (PDF page 23),
        # which leaves out elective deferrals (page 25); the Standard
        # Deduction Worksheet for Dependents' earned income subtracts Schedule
        # 1, line 15 (page 35).
        # PDF pages 23, 25, 35
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=23",
    )

    def formula(person, period, parameters):
        standard = parameters(period).gov.irs.deductions.standard
        filing_requirement = parameters(period).gov.irs.income.filing_requirement
        gross_income = person("medicaid_irs_gross_income", period)
        # Earned income is figured as on the IRS dependent worksheet, which
        # sets the limited standard deduction the gross income test compares
        # against: W-2 box 1 wages (which leave out elective deferrals) plus
        # earned disability benefits and business and farm income, minus
        # deductible self-employment tax, and not below zero.
        earned_income = max_(
            person("standard_deduction_worksheet_earned_income_person", period), 0
        )
        # Unearned income is gross income other than earned income (IRS Pub.
        # 501, Table 2). Gross income counts each source's positive amount, so
        # subtract those sources' positive amounts: a business loss does not
        # turn other income into unearned income.
        earned_gross_income = 0
        for source in filing_requirement.dependent.earned_income_sources:
            earned_gross_income += max_(0, person(source, period))
        earned_gross_income += person("earned_disability_benefits", period)
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
