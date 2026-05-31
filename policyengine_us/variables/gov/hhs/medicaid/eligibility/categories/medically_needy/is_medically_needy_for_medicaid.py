from policyengine_us.model_api import *


class is_medically_needy_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Medically needy"
    documentation = (
        "First-pass Medicaid medically needy/spenddown eligibility. This "
        "models aged, blind, and disabled people in states with a medically "
        "needy pathway for their category; applies state income and asset "
        "limits; and subtracts modeled medical expenses from countable income. "
        "It does not model non-ABD medically needy groups, state budget-period "
        "timing, anticipated-expense rules, or state-specific spenddown "
        "administration beyond the annual expense proxy."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/part-435/subpart-D"

    def formula(person, period, parameters):
        in_category = person("is_in_medicaid_medically_needy_category", period)
        is_aged_blind_or_disabled = person("is_ssi_aged_blind_disabled", period)
        personal_income = person("ssi_countable_income", period)
        medical_expenses = person("medicaid_medically_needy_medical_expenses", period)
        personal_assets = person("ssi_countable_resources", period)
        tax_unit = person.tax_unit
        income = tax_unit.sum(personal_income - medical_expenses)
        assets = tax_unit.sum(personal_assets)
        ma = parameters(period).gov.hhs.medicaid
        mn = ma.eligibility.categories.medically_needy
        is_joint = person.tax_unit("tax_unit_is_joint", period)
        state = person.household("state_code_str", period)
        income_limit = MONTHS_IN_YEAR * where(
            is_joint,
            mn.limit.income.couple[state],
            mn.limit.income.individual[state],
        )
        asset_limit = where(
            is_joint,
            mn.limit.assets.couple[state],
            mn.limit.assets.individual[state],
        )
        under_limits = (income <= income_limit) & (assets <= asset_limit)
        other_categories = [
            category
            for category in ma.eligibility.categories.covered
            if category != "is_medically_needy_for_medicaid"
        ]
        not_in_other_pathway = add(person, period, other_categories) == 0
        return (
            is_aged_blind_or_disabled
            & in_category
            & not_in_other_pathway
            & under_limits
        )
