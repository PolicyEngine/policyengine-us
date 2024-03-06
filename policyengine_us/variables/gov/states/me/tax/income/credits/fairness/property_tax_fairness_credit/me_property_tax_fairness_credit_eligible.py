from policyengine_us.model_api import *


class me_property_tax_fairness_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the maine property tax fairness credit"
    definition_period = YEAR
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        income = tax_unit(
            "me_sales_and_property_tax_fairness_credit_income", period
        )
        filing_status = tax_unit("filing_status", period)
        dependents = tax_unit("ctc_qualifying_children", period)
        capped_dependents = min_(dependents, 2)
        p = parameters(
            period
        ).gov.states.me.tax.income.credits.fairness.property_tax
        income_threshold = p.income_limit[filing_status][capped_dependents]
        return income < income_threshold
