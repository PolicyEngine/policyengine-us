from policyengine_us.model_api import *


class is_irs_aged(Variable):
    value_type = bool
    entity = Person
    label = "Aged person under the IRS requirements"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/63#f"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.standard.aged_or_blind
        return tax_unit("age", period) >= p.age_threshold
