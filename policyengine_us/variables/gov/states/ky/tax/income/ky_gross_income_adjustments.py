from policyengine_us.model_api import *


class ky_gross_income_adjustments(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky gross income adjustments "
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY
    
    def formula(tax_unit, period, parameters):
        status = tax_unit("filer_status", period)
        age = tax_unit("age", period)
        blind = tax_unit("blind", period)

        # Get the parameter values
        params = parameters(period).tax.KY.age_threshold

        if status == "single":
            if age < 65:
                return params.single.under_65
            elif blind:
                return params.single.over_65_and_blind
            else:
                return params.single.over_65_or_blind
        else: # assuming status is "joint"
            if age < 65:
                return params.joint.both_under_65_or_over
            elif blind:
                return params.joint.both_over_65
            else:
                return params.joint.one_over_65