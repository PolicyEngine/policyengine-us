from policyengine_us.model_api import *


class wy_lieap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for modeled Wyoming LIEAP"
    documentation = (
        "Models residence, qualifying-member count, income and primary heating "
        "responsibility. A positive reported heating expense, or heat included "
        "in rent, establishes responsibility for the primary heating cost. "
        "Winter presence, work registration, tribal program routing, "
        "institutional exclusions and application verification are not "
        "separately observed."
    )
    reference = (
        # FY2026 State Plan, sections 1.4, 2.1 and 2.3, PDF pages 5,8.
        "https://dfs.wyo.gov/wp-content/uploads/2025/10/FFY2026-LIEAP-State-Model-Plan.pdf#page=5",
        # Rule 3(kk).
        "https://www.law.cornell.edu/regulations/wyoming/agency-049/subagency-0024/chapter-1/049-1-Wyo-Code-R-SSSS-1-3",
        # Rule 7.
        "https://www.law.cornell.edu/regulations/wyoming/agency-049/subagency-0024/chapter-1/049-1-Wyo-Code-R-SSSS-1-7",
        # Rule 8(b).
        "https://www.law.cornell.edu/regulations/wyoming/agency-049/subagency-0024/chapter-1/049-1-Wyo-Code-R-SSSS-1-8",
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
    )
    defined_for = StateCode.WY

    def formula(spm_unit, period, parameters):
        # Follows FY2026 plan section 1.4, which elects no categorical eligibility;
        # rules 7(a)(i) list POWER, SNAP and veteran or survivor pension recipients.
        size = spm_unit("wy_lieap_household_size", period)
        income = spm_unit("wy_lieap_countable_income", period)
        limit = spm_unit("wy_lieap_income_limit", period)
        floor_rate = parameters(period).gov.hhs.liheap.fpg_floor
        guideline = spm_unit("wy_lieap_fpg", period).astype(np.float64)
        federal_floor = np.round(guideline * floor_rate, 2)
        income_eligible = (income <= limit) | (income < federal_floor)
        # Rule 8(b)(i) makes a household vulnerable when it is billed for or
        # pays its heating fuel, or when its rent includes a prorated heating
        # cost; rule 3(kk) allows the energy purchase to be in the form of rent.
        responsible = (spm_unit("heating_expense", period) > 0) | spm_unit(
            "heat_expense_included_in_rent", period
        )
        return (size > 0) & income_eligible & responsible
