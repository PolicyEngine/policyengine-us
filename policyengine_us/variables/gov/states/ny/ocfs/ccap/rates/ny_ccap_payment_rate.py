from policyengine_us.model_api import *


class ny_ccap_payment_rate(Variable):
    value_type = float
    entity = Person
    label = "New York CCAP monthly payment before family share"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.NY
    documentation = (
        "Applies the combined differential to the lesser of the child's "
        "expenses and applicable market rate. Under 24-OCFS-LCM-22, the "
        "result can exceed the provider's charge. Legally exempt group "
        "payments cannot exceed the corresponding day care center rate."
    )
    reference = (
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.9",
        "https://ocfs.ny.gov/main/policies/external/2024/lcm/24-OCFS-LCM-22.pdf#page=9",
    )

    def formula(person, period, parameters):
        expenses = person("ny_ccap_childcare_expenses", period)
        market_rate = person("ny_ccap_market_rate", period)
        differential = person("ny_ccap_differential", period)
        payment = min_(expenses, market_rate) * (1 + differential)
        provider = person("childcare_provider_type_group", period.this_year)
        group_provider = provider == provider.possible_values.LE_GC
        center_rate = person("ny_ccap_day_care_center_rate", period)
        return where(group_provider, min_(payment, center_rate), payment)
