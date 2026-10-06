from policyengine_us.model_api import *


class wy_lieap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for modeled Wyoming LIEAP"
    documentation = (
        "Models residence, qualifying-member count, income and primary heating "
        "responsibility. Positive reported heating expense represents the unit's "
        "eligible seasonal bill or documented heat-in-rent share. Winter presence, "
        "work registration, tribal program routing, institutional exclusions and "
        "application verification are not separately observed."
    )
    reference = (
        "https://dfs.wyo.gov/wp-content/uploads/2025/10/FFY2026-LIEAP-State-Model-Plan.pdf#page=8",
        # Chapter 1, sections 7 and 8(b).
        "https://rules.wyo.gov/Search.aspx?mode=7",
    )
    defined_for = StateCode.WY

    def formula(spm_unit, period, parameters):
        size = spm_unit("wy_lieap_household_size", period)
        income = spm_unit("wy_lieap_countable_income", period)
        limit = spm_unit("wy_lieap_income_limit", period)
        expense = spm_unit("heating_expense", period)
        return (size > 0) & (income <= limit) & (expense > 0)
