from policyengine_us.model_api import *


class tx_ceap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas Comprehensive Energy Assistance Program (CEAP) benefit"
    unit = USD
    definition_period = YEAR
    defined_for = "tx_ceap_eligible"
    reference = (
        "https://www.tdhca.texas.gov/sites/default/files/community-affairs/ceap/docs/24-LIHEAP-Plan.pdf#page=11",
        "https://www.tdhca.texas.gov/sites/default/files/community-affairs/docs/25-LIHEAP-Plan-DRAFT_0.pdf",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.tdhca.ceap.utility_assistance

        income = add(spm_unit, period, ["irs_gross_income"])
        fpg = spm_unit("spm_unit_fpg", period)

        # Determine FPG ratio for income bracket
        fpg_ratio = where(fpg > 0, income / fpg, 0)

        # Maximum utility assistance by income bracket
        # per 10 TAC 6.309(e).
        max_amount = select(
            [
                fpg_ratio <= p.income_bracket.low,
                fpg_ratio <= p.income_bracket.mid,
            ],
            [
                p.max_amount.low_income,
                p.max_amount.mid_income,
            ],
            default=p.max_amount.high_income,
        )

        # Benefit is capped by actual energy expenses
        energy_expenses = add(
            spm_unit,
            period,
            ["electricity_expense", "gas_expense"],
        )

        return min_(max_amount, energy_expenses)
