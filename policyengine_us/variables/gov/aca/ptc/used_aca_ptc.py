from policyengine_us.model_api import *


class used_aca_ptc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Used ACA premium tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/26/1.36B-3#d_1"

    def formula(tax_unit, period, parameters):
        # The credit cannot exceed the enrollment premiums of the coverage
        # family (26 CFR 1.36B-3(d)(1)(i)); an enrollee outside the tax family
        # pays their own share of the policy.
        return min_(
            tax_unit("aca_ptc", period),
            tax_unit("aca_ptc_coverage_family_premium", period),
        )
