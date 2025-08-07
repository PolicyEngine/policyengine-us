from policyengine_us.model_api import *


class ok_military_retirement_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma military retirement exclusion"
    unit = USD
    definition_period = YEAR
    reference = (
        # (g)
        "https://casetext.com/regulation/oklahoma-administrative-code/title-710-oklahoma-tax-commission/chapter-50-income/subchapter-15-oklahoma-taxable-income/part-5-other-adjustments-to-income/section-71050-15-49-deduction-for-retirement-income",
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ok.tax.income.agi.subtractions.military_retirement
        military_retirement_benefits = tax_unit.members(
            "military_retirement_pay", period
        )
        adjust_military_retirement_amount = (
            military_retirement_benefits * p.rate
        )
        capped_exclusion_amount = max_(
            p.floor, adjust_military_retirement_amount
        )
        return tax_unit.sum(
            min_(military_retirement_benefits, capped_exclusion_amount)
        )
