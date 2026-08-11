from policyengine_us.model_api import *


class me_property_tax_fairness_credit_countable_rent(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Countable rent for Maine property tax fairness credit"
    definition_period = YEAR
    defined_for = StateCode.ME
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_pstfc_ff.pdf#page=2"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.me.tax.income.credits.fairness.property_tax
        rent = add(tax_unit, period, ["rent"])
        utilities_included_in_rent = tax_unit("utilities_included_in_rent", period)
        utility_expenses = add(tax_unit, period, ["utility_expense"])
        # Schedule PTFC/STFC line 5c: when rent includes heat/utilities, exclude
        # the utility portion before taking 15% of rent. If the amount is known,
        # subtract it; if it is not known, subtract 15% of gross rent instead.
        amount_known = utility_expenses > 0
        deductible_utility_expenses = utilities_included_in_rent * where(
            amount_known, utility_expenses, rent * p.rate.utilities_included_in_rent
        )
        net_rent = rent - deductible_utility_expenses
        return net_rent * p.rate.rent
