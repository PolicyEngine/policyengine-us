from policyengine_us.model_api import *


class is_optional_senior_or_disabled_asset_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Asset-eligibility for State’s optional Medicaid pathway for seniors or people with disabilities"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a#m"

    def formula(person, period, parameters):
        #  Assets
        personal_assets = person("ssi_countable_resources", period)  # $
        tax_unit = person.tax_unit
        assets = tax_unit.sum(personal_assets)

        #  state info
        is_joint = tax_unit("tax_unit_is_joint", period)
        state = person.household("state_code_str", period)

        #  Parameters
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled

        #  Asset limit
        asset_limit = where(
            is_joint,
            p.assets.limit.couple[state],
            p.assets.limit.individual[state],
        )

        return assets < asset_limit
