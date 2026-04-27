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
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.deductions.standard
        gross_income = person("medicaid_irs_gross_income", period)
        earned_income = person("earned_income", period)
        unearned_income = gross_income - earned_income

        married = person.marital_unit.nb_persons() == 2
        filing_status = where(married, FilingStatus.SEPARATE, FilingStatus.SINGLE)
        aged_or_blind_count = (
            person("age", period.this_year) >= p.aged_or_blind.age_threshold
        ).astype(int) + person("is_blind", period).astype(int)
        additional_deduction = (
            p.aged_or_blind.amount[filing_status] * aged_or_blind_count
        )
        regular_standard_deduction = p.amount[filing_status]
        dependent_standard_deduction = (
            min_(
                regular_standard_deduction,
                max_(
                    p.dependent.amount,
                    p.dependent.additional_earned_income + earned_income,
                ),
            )
            + additional_deduction
        )
        spouse_itemizes = married & person.tax_unit("separate_filer_itemizes", period)

        return (
            (spouse_itemizes & (gross_income >= 5))
            | (unearned_income > (p.dependent.amount + additional_deduction))
            | (earned_income > (regular_standard_deduction + additional_deduction))
            | (gross_income > dependent_standard_deduction)
        )
