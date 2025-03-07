from policyengine_us.model_api import *


class ma_tafdc_income_limit(Variable):
    value_type = float
    unit = USD
    entity = TaxUnit
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) payment standard"
    definition_period = MONTH
    reference = "https://www.masslegalservices.org/content/75-how-much-will-you-get-each-month"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ma.dta.tafdc.eligibility.income_limit.teen_parent
        teen_parent_present = tax_unit.any(
            tax_unit.members("ma_tafdc_eligible_teen_parent", period)
        )

        base_payment_standard = tax_unit("ma_tafdc_payment_standard", period)
        # Calculate the base income limit for teen parents
        fpg = tax_unit("tax_unit_fpg", period)
        teen_parent_income_limit = fpg * p.fpg_limit
        # Select the appropriate income limit based on whether there is a teen parent
        return where(
            teen_parent_present,
            teen_parent_income_limit,
            base_payment_standard,
        )
