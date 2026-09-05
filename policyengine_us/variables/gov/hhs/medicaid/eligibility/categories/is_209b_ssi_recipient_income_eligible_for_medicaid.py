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
        # Missouri budgets a married couple living together jointly,
        # whatever their filing status (DSS Manual § 0805.015.05).
        is_mo = person.household("state_code", period) == StateCode.MO
        income_less_expenses = personal_income - medical_expenses
        income_after_spenddown = where(
            is_mo,
            person.marital_unit.sum(income_less_expenses),
            person.tax_unit.sum(income_less_expenses),
        )

        income_limit = person(
            "medicaid_optional_senior_or_disabled_income_limit", period
        )
        return income_eligible | (income_after_spenddown <= income_limit)
