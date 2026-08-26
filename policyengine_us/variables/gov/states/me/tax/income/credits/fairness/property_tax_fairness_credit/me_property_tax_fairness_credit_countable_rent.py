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
        # utilities_included_in_rent is a TaxUnit boolean (it lives in the
        # household/ folder but is defined on the TaxUnit entity), used here as a
        # proxy for Schedule PTFC/STFC line 5b (does rent paid include heat,
        # utilities, furniture, or similar items?).
        # Related sibling flag: heat_expense_included_in_rent (an SPMUnit bool used
        # by MA/IL LIHEAP) overlaps line 5b, but it is NOT OR'd into this gate. A
        # heat-only household (heat_expense_included_in_rent: true /
        # utilities_included_in_rent: false) must set utilities_included_in_rent to
        # answer line 5b "Yes". OR-ing the flags is deferred: it would be a
        # cross-entity (SPMUnit -> TaxUnit) change and is a design call.
        included = tax_unit("utilities_included_in_rent", period)
        # Line 5c: the amount of heat, utilities, furniture, or similar items
        # included in rent paid (line 5a). A zero here is a sentinel meaning the
        # amount is unknown, so we subtract the 15%-of-rent estimate instead of a
        # known dollar amount. This is distinct from the household's general
        # utility_expense (separately-paid utilities), which is not subtracted.
        included_amount = tax_unit(
            "me_property_tax_fairness_credit_utilities_in_rent_amount", period
        )
        utility_portion = included * where(
            included_amount > 0,
            included_amount,
            rent * p.rate.utilities_share_of_rent,
        )
        # Clamp guards inconsistent user input: on the unknown branch the base is
        # 0.85 * line 5a (always non-negative), and on the known branch line 5c is
        # a component of line 5a, so a subtraction below zero reflects bad input.
        net_rent = max_(rent - utility_portion, 0)
        return net_rent * p.rate.rent
