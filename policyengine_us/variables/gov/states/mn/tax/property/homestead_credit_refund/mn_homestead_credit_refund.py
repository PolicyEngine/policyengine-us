from policyengine_us.model_api import *


class mn_homestead_credit_refund(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota Homestead Credit Refund"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290A.04",
        "https://www.taxformfinder.org/forms/2024/2024-minnesota-form-m1pr-instructions.pdf#page=23",
        "https://www.taxformfinder.org/forms/2025/2025-minnesota-form-m1pr-instructions.pdf#page=23",
    )
    defined_for = "mn_homestead_credit_refund_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.property.homestead_credit_refund
        household_income = max_(
            0, tax_unit("mn_homestead_credit_refund_household_income", period)
        )
        property_tax = add(tax_unit, period, ["real_estate_taxes"])
        excess_property_tax = max_(
            0,
            property_tax
            - household_income * p.percent_of_income.calc(household_income),
        )
        refund = excess_property_tax * p.refund_rate.calc(household_income)
        return round_(min_(refund, p.max_refund.calc(household_income)))
