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
        included = tax_unit("utilities_included_in_rent", period)
        # Dedicated amount of utilities included in rent (Schedule PTFC/STFC
        # line 5c). This is distinct from the household's general utility_expense
        # (separately-paid utilities), which is not subtracted from rent here.
        included_amount = tax_unit("me_ptfc_utilities_included_in_rent", period)
        # Schedule PTFC/STFC line 5c: when rent includes heat/utilities, exclude
        # the utility portion before taking 15% of rent. If the included amount
        # is known (> 0), subtract it; if it is not known (0), subtract the
        # 15%-of-rent estimate instead. When utilities are not included in rent,
        # nothing is subtracted.
        amount_known = included_amount > 0
        utility_portion = included * where(
            amount_known,
            included_amount,
            rent * p.rate.utilities_included_in_rent,
        )
        # Line 5d (5a - 5c) can never be negative.
        net_rent = max_(rent - utility_portion, 0)
        return net_rent * p.rate.rent
