from openfisca_us.model_api import *


class is_medically_needy_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Medically needy"
    definition_period = YEAR

    def formula(person, period, parameters):
        in_category = person("is_in_medicaid_medically_needy_category", period)
        personal_income = person("ssi_countable_income", period)
        medical_expenses = person("medical_out_of_pocket_expenses", period)
        personal_assets = person("ssi_countable_resources", period)
        tax_unit = person.tax_unit
        income = tax_unit.sum(personal_income - medical_expenses)
        assets = tax_unit.sum(personal_assets)
        ma = parameters(
            period
        ).hhs.medicaid.eligibility.categories.medically_needy
        is_joint = person.tax_unit("tax_unit_is_joint", period)
        state = person.household("state_code_str", period)
        income_limit = where(
            is_joint,
            ma.limit.income.couple[state],
            ma.limit.income.individual[state],
        )
        asset_limit = where(
            is_joint,
            ma.assets.limit.couple[state],
            ma.assets.limit.individual[state],
        )
        under_limits = (income < income_limit) & (
            assets < asset_limit
        )
        return in_category & under_limits