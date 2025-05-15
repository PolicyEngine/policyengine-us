from policyengine_us.model_api import *


class il_aabd_financial_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Illinois Aid to the Aged, Blind or Disabled (AABD) eligible person due to financial criteria"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        asset_eligible = person.spm_unit(
            "il_aabd_asset_value_eligible", period
        )
        total_needs = person("il_aabd_need_standard_person", period)
        countable_income = person("il_aabd_countable_income", period)
        income_eligible = total_needs >= countable_income
        return income_eligible & asset_eligible
