from policyengine_us.model_api import *


class md_hundred_year_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland hundred year exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://trackbill.com/bill/maryland-house-bill-186-income-tax-subtraction-modification-for-centenarians/2173534/"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        eligible = tax_unit("md_hundred_year_exemption_eligible", period)
        return (
            where(
                eligible, 
                p.amount,
                0
            )
        )
