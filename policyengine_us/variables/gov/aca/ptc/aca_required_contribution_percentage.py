from policyengine_us.model_api import *


class aca_required_contribution_percentage(Variable):
    value_type = float
    entity = TaxUnit
    label = "ACA PTC phase-out rate (i.e., IRS Form 8962 'applicable figure')"
    unit = "/1"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/36B#b_3_A"

    def formula(tax_unit, period, parameters):
        magi_frac = tax_unit("aca_magi_fraction", period)
        p = parameters(period).gov.aca.required_contribution_percentage
        return np.interp(magi_frac, p.thresholds, p.amounts)
