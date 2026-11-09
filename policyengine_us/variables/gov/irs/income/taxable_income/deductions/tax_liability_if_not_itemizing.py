from policyengine_us.model_api import *
from policyengine_core.tracers import SimpleTracer


class tax_liability_if_not_itemizing(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax liability if not itemizing"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        branch = get_itemization_branch(tax_unit, period, itemizes=False)
        return branch.calculate("income_tax", period)
