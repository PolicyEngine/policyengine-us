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
        filing_status = tax_unit("filing_status", period)
        dependents = tax_unit("ctc_qualifying_children", period)
        capped_dependents = min_(dependents, p.dependent_count_threshold)
        benefit_base = p.amount[filing_status][capped_dependents]
        countable_rent_property_tax = tax_unit(
            "me_property_tax_fairness_credit_countable_rent_property_tax",
            period,
        )
        capped_benefit_base = min_(benefit_base, countable_rent_property_tax)
        income = tax_unit(
            "me_sales_and_property_tax_fairness_credit_income", period
        )
        income_rate = income * p.rate.income
        uncapped_credit = max_(capped_benefit_base - income_rate, 0)
        greater_age_head_spouse = tax_unit("greater_age_head_spouse", period)
        cap = p.cap.calc(greater_age_head_spouse)

        return min_(uncapped_credit, cap)
