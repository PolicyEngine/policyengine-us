from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_budget_total,
    _ssi_couple_total,
)


class is_209b_ssi_recipient_income_eligible_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "209(b) income eligibility for Medicaid"
    documentation = (
        "Whether this person satisfies the income test for Medicaid through a "
        "Section 209(b) state's more restrictive aged, blind, or disabled "
        "criteria, including spenddown of incurred medical expenses. It "
        "decides SSI recipients in every 209(b) state, and people who do not "
        "receive SSI in a 209(b) state with no medically needy program."
    )
    definition_period = YEAR
    reference = (
        "https://www.medicaid.gov/resources-for-states/downloads/macpro-ig-more-restrictive-requirements-1902f-209bstates.pdf#page=3",
        "https://www.govinfo.gov/link/cfr/42/435?link-type=pdf&sectionnum=121&year=mostrecent",
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-020-00/0805-020-15/",
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
        # 42 CFR 435.121(f)(1)(iii) also deducts the expenses of financially
        # responsible relatives, and MHABD 0805.020.15 names a child's parents.
        parental_expense_share = person(
            "medicaid_parental_medical_expense_share", period
        )
        # SSI financial responsibility rules (42 CFR 435.602): the unit is
        # the individual or the married couple, not the tax filing unit.
        budget = personal_income - medical_expenses - parental_expense_share
        income_after_spenddown = where(
            person("ssi_couple_computation_applies", period),
            _ssi_couple_budget_total(person, period, budget),
            _ssi_couple_total(person, period, budget),
        )

        # The limit is per person (Missouri's blind standard can differ
        # within a couple) while the income is the couple's combined total.
        income_limit = person(
            "medicaid_optional_senior_or_disabled_income_limit", period
        )
        return income_eligible | (income_after_spenddown <= income_limit)
