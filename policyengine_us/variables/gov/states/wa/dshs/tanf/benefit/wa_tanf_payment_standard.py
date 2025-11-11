from policyengine_us.model_api import *


class wa_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington TANF payment standard"
    unit = USD
    definition_period = MONTH
    reference = ("https://app.leg.wa.gov/wac/default.aspx?cite=388-478-0020",)
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        # Get payment standard parameters by family size
        # Per WAC 388-478-0020, payment standards are approximately 33%
        # of the Federal Poverty Level (updated January 1, 2024)
        p = parameters(period).gov.states.wa.dshs.tanf
        payment_standards = p.benefit.payment_standard
        max_family_size = p.maximum_family_size

        # Get assistance unit size, capped at maximum table value (10)
        size = spm_unit("spm_unit_size", period)
        size_capped = min_(size, max_family_size)

        # Look up payment standard for this family size
        # Ranges from $450/month (1 person) to $1,662/month (10+ people)
        payment_standard = payment_standards[size_capped]

        return payment_standard
