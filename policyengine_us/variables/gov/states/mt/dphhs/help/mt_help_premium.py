from policyengine_us.model_api import *


class mt_help_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana HELP annual premium"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        "https://www.medicaid.gov/Medicaid-CHIP-Program-Information/By-Topics/Waivers/1115/downloads/mt/HELP-program/mt-HELP-program-help-ops-prtcl-03012016.pdf#page=2",
        "https://dphhs.mt.gov/HELPPlan/MT2022helpExpanQ4-annNarrB.pdf#page=4",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.dphhs.help.premium
        if not p.active:
            return 0

        income_level = tax_unit("tax_unit_medicaid_income_level", period)
        in_income_range = (income_level >= p.income_threshold.lower) & (
            income_level <= p.income_threshold.upper
        )
        has_help_adult = tax_unit.sum(tax_unit.members("is_mt_help_adult", period)) > 0
        income = tax_unit("medicaid_magi", period)
        return where(in_income_range & has_help_adult, income * p.rate, 0)
