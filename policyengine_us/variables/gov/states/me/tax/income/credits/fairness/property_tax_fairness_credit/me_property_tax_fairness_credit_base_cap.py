from policyengine_us.model_api import *


class me_property_tax_fairness_credit_base_cap(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Maine property tax fairness credit base cap"
    definition_period = YEAR
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.me.tax.income.credits.fairness.property_tax

        benefit_base = tax_unit(
            "me_property_tax_fairness_credit_benefit_base", period
        )

        greater_age_head_spouse = tax_unit("greater_age_head_spouse", period)
        senior_benefit_base = p.benefit_base.senior.calc(
            greater_age_head_spouse
        )
        senior_benefit_apply = senior_benefit_base != 0
        adjusted_benefit_base = where(
            senior_benefit_apply, senior_benefit_base, benefit_base
        )

        countable_rent_property_tax = tax_unit(
            "me_property_tax_fairness_credit_countable_rent_property_tax",
            period,
        )
        capped_benefit_base = min_(
            adjusted_benefit_base, countable_rent_property_tax
        )
        income = tax_unit(
            "me_sales_and_property_tax_fairness_credit_income", period
        )
        income_rate = income * p.rate.income
        uncapped_credit = max_(capped_benefit_base - income_rate, 0)
        cap = p.cap.calc(greater_age_head_spouse)

        return min_(uncapped_credit, cap)
