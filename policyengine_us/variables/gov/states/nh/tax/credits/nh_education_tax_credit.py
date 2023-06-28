from policyengine_us.model_api import *


class nh_education_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire Education Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.gencourt.state.nh.us/rsa/html/NHTOC/NHTOC-V-77-G.htm"
    )
    defined_for = StateCode.NH

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nh.tax.credits.education

        # Get Rate for donation
        donation = add(
            tax_unit,
            period,
            ["charitable_cash_donations", "charitable_non_cash_donations"],
        )
        return p.rate.calc(donation)
