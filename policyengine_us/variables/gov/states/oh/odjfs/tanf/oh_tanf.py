from policyengine_us.model_api import *


class oh_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Ohio TANF"
    unit = USD
    definition_period = YEAR
    defined_for = "oh_tanf_eligible"
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5107.10",
        "http://codes.ohio.gov/oac/5101:1-23-40",
    )

    def formula(spm_unit, period, parameters):
        # Get payment standard for assistance group size
        payment_standard = spm_unit("oh_tanf_payment_standard", period)

        # Get countable income (after all disregards)
        countable_income = spm_unit("oh_tanf_countable_income", period)

        # Calculate benefit: Payment Standard - Countable Income
        # Per OAC 5101:1-23-40: "OWF payments are payments made to an
        # assistance group which represent the difference between the
        # countable income and the appropriate OWF payment standard."
        benefit = payment_standard - countable_income

        # Apply minimum benefit threshold
        # Per OAC 5101:1-23-40: "OWF shall not be authorized when the
        # amount is at least $1 but less than $10 per month"
        p = parameters(period).gov.states.oh.odjfs.tanf
        minimum_benefit = p.minimum_benefit * MONTHS_IN_YEAR

        # If benefit is positive but below minimum, set to zero
        benefit_meets_minimum = (benefit >= minimum_benefit) | (benefit <= 0)
        benefit = where(benefit_meets_minimum, benefit, 0)

        # Benefit cannot be negative
        return max_(benefit, 0)
