from openfisca_us.model_api import *


class is_optional_senior_or_disabled_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Seniors or disabled people not meeting SSI rules"
    documentation = "Whether this person can claim Medicaid through the State's optional pathway for seniors or people with disabilities."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a#m"

    def formula(person, period, parameters):
        personal_income = person("ssi_countable_income", period)
        personal_assets = person("ssi_countable_resources", period)
        tax_unit = person.tax_unit
        income = tax_unit.sum(personal_income)
        assets = tax_unit.sum(personal_assets)
        ma = parameters(
            period
        ).hhs.medicaid.eligibility.categories.senior_or_disabled
        is_senior_or_disabled = person("is_ssi_aged_blind_disabled", period)
        is_joint = person.tax_unit("tax_unit_is_joint", period)
        state = person.household("state_code_str", period)
        income_limit = where(
            is_joint,
            ma.income.limit.couple[state] * MONTHS_IN_YEAR,
            ma.income.limit.individual[state] * MONTHS_IN_YEAR,
        )
        income_disregard = where(
            is_joint,
            ma.income.disregard.couple[state] * MONTHS_IN_YEAR,
            ma.income.disregard.individual[state] * MONTHS_IN_YEAR,
        )
        asset_limit = where(
            is_joint,
            ma.assets.limit.couple[state],
            ma.assets.limit.individual[state],
        )
        under_limits = (income - income_disregard < income_limit) & (
            assets < asset_limit
        )
        return is_senior_or_disabled & under_limits
