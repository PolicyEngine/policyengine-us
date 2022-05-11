from openfisca_us.model_api import *


class meets_medicaid_disabled_asset_test(Variable):
    value_type = bool
    entity = Person
    label = "Meets Medicaid disabled asset test"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        assets = person.spm_unit("spm_unit_assets", period)
        limit = parameters(period).hhs.medicaid.aged_or_disabled.asset_limit
        state = person.household("state_code_str", period)
        return assets <= limit[state]
