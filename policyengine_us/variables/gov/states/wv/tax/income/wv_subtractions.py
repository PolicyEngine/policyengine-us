from policyengine_us.model_api import *


class wv_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia subtractions from the adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wv.tax.income.subtractions
        # Dependents' income is not in federal AGI; they report it on their
        # own return, so person-level subtractions count only the head and
        # spouse.
        total_subtractions = tax_unit_non_dep_add(tax_unit, period, p.subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
