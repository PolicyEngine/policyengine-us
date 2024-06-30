from policyengine_us.model_api import *


class me_property_tax_fairness_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the maine property tax fairness credit"
    definition_period = YEAR
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.me.tax.income.credits.fairness.property_tax
        benefit_base = tax_unit(
            "me_property_tax_fairness_credit_benefit_base", period
        )
        income_threshold = benefit_base / p.rate.income
        income = tax_unit(
            "me_sales_and_property_tax_fairness_credit_income", period
        )
        income_eligible = income < income_threshold
        # Separate filers are ineligible
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        separate = filing_status == filing_statuses.SEPARATE

        return income_eligible & ~separate
