from policyengine_us.model_api import *


class va_capped_state_and_local_sales_or_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Capped state and local sales or income tax for Virginia itemized deductions purposes"
    unit = USD

    def formula(tax_unit, period, parameters):
        uncapped_state_and_local_tax = tax_unit(
            "state_and_local_sales_or_income_tax", period
        )
        p_salt = parameters(
            period
        ).gov.irs.deductions.itemized.salt_and_real_estate
        filing_status = tax_unit("filing_status", period)
        real_estate_tax = add(tax_unit, period, ["real_estate_taxes"])
        state_and_local_tax_cap = p_salt.cap[filing_status]
        cap_reduced_by_real_estate_tax = max_(
            state_and_local_tax_cap - real_estate_tax, 0
        )
        return min_(
            uncapped_state_and_local_tax, cap_reduced_by_real_estate_tax
        )
