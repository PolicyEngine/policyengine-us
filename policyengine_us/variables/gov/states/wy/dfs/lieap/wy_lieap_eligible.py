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
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
    )
    defined_for = StateCode.WY

    def formula(spm_unit, period, parameters):
        size = spm_unit("wy_lieap_household_size", period)
        income = spm_unit("wy_lieap_countable_income", period)
        limit = spm_unit("wy_lieap_income_limit", period)
        floor_rate = parameters(period).gov.hhs.liheap.fpg_floor
        guideline = spm_unit("wy_lieap_fpg", period).astype(np.float64)
        federal_floor = np.round(guideline * floor_rate, 2)
        income_eligible = (income <= limit) | (income < federal_floor)
        expense = spm_unit("heating_expense", period)
        return (size > 0) & income_eligible & (expense > 0)
