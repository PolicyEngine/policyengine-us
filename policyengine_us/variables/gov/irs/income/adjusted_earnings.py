from policyengine_us.model_api import *


class adjusted_earnings(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Personal earned income adjusted for self-employment tax"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/32#c_2_A"

    def formula(person, period, parameters):
        # Per IRC 32(c)(2)(A), EITC earned income = wages + net SE earnings
        # (within the meaning of IRC 1402(a)), determined with regard to
        # the IRC 164(f) deduction (one-half of SE tax).
        #
        # Per IRS EIC Worksheet B (Form 1040 Instructions), Line 4b:
        # "Combine lines 1e, 2c, 3, and 4a" — SE losses reduce earned
        # income with no per-person floor. The floor at zero applies only
        # to the combined tax-unit total (see filer_adjusted_earnings).
        #
        # Per IRS Form 2441 instructions (CDCC): "You must reduce your
        # earned income by any loss from self-employment."
        p = parameters(period).gov.irs.ald.misc
        adjustment = (
            (1 - p.self_emp_tax_adj)
            * p.employer_share
            * person("self_employment_tax", period)
        )
        return person("earned_income", period) - adjustment
