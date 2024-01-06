from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit_net_household_income(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Net household income for Montana elderly homeowner or renter credit"
    )
    unit = USD
    definition_period = YEAR
    defined_for = "mt_elderly_homeowner_or_renter_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.credits.elderly_homeowner_or_renter
        # Only one claim is allowed per household
        # married taxpayer who are living apart may qualify for only one credit per year
        standard_exclusion = p.net_household_income.standard_exclusion
        gross_household_income = tax_unit(
            "mt_elderly_homeowner_or_renter_credit_gross_household_income",
            period,
        )
        reduced_household_income = max_(
            gross_household_income - standard_exclusion, 0
        )
        reduction_rate = p.net_household_income.reduction_rate.calc(
            reduced_household_income
        )
        return reduced_household_income * reduction_rate
