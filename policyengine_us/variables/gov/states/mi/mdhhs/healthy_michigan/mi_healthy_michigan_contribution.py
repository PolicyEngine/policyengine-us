from policyengine_us.model_api import *


class mi_healthy_michigan_contribution(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan Healthy Michigan Plan annual contribution"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI
    reference = (
        "https://www.medicaid.gov/Medicaid-CHIP-Program-Information/By-Topics/Waivers/1115/downloads/mi/Healthy-Michigan/mi-healthy-michigan-waiver-amend-req-11082013.pdf#page=13",
        "https://www.michigan.gov/healthymiplan",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mi.mdhhs.healthy_michigan.contribution
        if not p.active:
            return 0

        income_level = tax_unit("tax_unit_medicaid_income_level", period)
        in_income_range = (income_level > p.income_threshold.lower) & (
            income_level <= p.income_threshold.upper
        )
        has_hmp_adult = (
            tax_unit.sum(tax_unit.members("is_mi_healthy_michigan_adult", period)) > 0
        )
        income = tax_unit("medicaid_magi", period)
        return where(in_income_range & has_hmp_adult, income * p.rate, 0)
