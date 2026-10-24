from policyengine_us.model_api import *


class wa_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for modeled Washington LIHEAP"
    documentation = (
        "Models state residence, income, qualified-member count and heating "
        "responsibility. Heat included in rent can establish responsibility "
        "without a reported cost; the award remains unsupported until a cost "
        "is supplied. No asset test or categorical subsidy exclusion applies. "
        "Prior receipt in the current season and application verification are "
        "not observed."
    )
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/WA_Plan_2026.pdf#page=8",
        "https://deptofcommerce.app.box.com/s/3fp0xz4y2x2p4hedw9ww4sk7ma36srlx",
    )
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        size = spm_unit("wa_liheap_household_size", period)
        income = spm_unit("wa_liheap_countable_income", period)
        limit = spm_unit("wa_liheap_income_limit", period)
        expense = spm_unit("heating_expense", period)
        included_in_rent = spm_unit("heat_expense_included_in_rent", period)
        heating_type = spm_unit("heating_type", period)
        has_heating = heating_type != heating_type.possible_values.NONE
        return (
            (size > 0)
            & (income <= limit)
            & ((expense > 0) | included_in_rent)
            & has_heating
        )
