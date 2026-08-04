from policyengine_us.model_api import *


class is_209b_ssi_recipient_income_eligible_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "209(b) SSI-recipient income eligibility for Medicaid"
    documentation = (
        "Whether this SSI recipient satisfies the income test for Medicaid "
        "through a Section 209(b) state's more restrictive aged, blind, or "
        "disabled criteria, including spenddown of incurred medical expenses."
    )
    definition_period = YEAR
    reference = (
        "https://www.medicaid.gov/resources-for-states/downloads/macpro-ig-more-restrictive-requirements-1902f-209bstates.pdf#page=3",
        "https://www.govinfo.gov/link/cfr/42/435?link-type=pdf&sectionnum=121&year=mostrecent",
    )

    def formula(person, period, parameters):
        income_eligible = person(
            "is_optional_senior_or_disabled_income_eligible", period
        )
        personal_income = person(
            "medicaid_optional_senior_or_disabled_countable_income", period
        )
        # The countable-income measure does not add modeled SSI or state
        # supplement benefits, so apply the remaining 435.121 spenddown here.
        medical_expenses = person("medicaid_medically_needy_medical_expenses", period)
        tax_unit = person.tax_unit
        income_after_spenddown = tax_unit.sum(personal_income - medical_expenses)

        is_joint = tax_unit("tax_unit_is_joint", period)
        state = person.household("state_code_str", period)
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled
        income_limit_pct = where(
            is_joint,
            p.income.limit.couple[state],
            p.income.limit.individual[state],
        )
        income_limit = income_limit_pct * tax_unit("tax_unit_fpg", period)
        return income_eligible | (income_after_spenddown <= income_limit)
