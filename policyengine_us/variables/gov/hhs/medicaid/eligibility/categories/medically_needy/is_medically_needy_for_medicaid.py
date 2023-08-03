from policyengine_us.model_api import *


class is_medically_needy_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Medically needy"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/part-435/subpart-D"

    def formula(person, period, parameters):
        in_category = person("is_in_medicaid_medically_needy_category", period)
        personal_income = person("ssi_countable_income", period)
        medical_expenses = person("medical_out_of_pocket_expenses", period)
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
        return in_category & not_in_other_pathway & under_limits
