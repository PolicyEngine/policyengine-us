"""
Connecticut TFA payment standard by region and household size.
"""

from policyengine_us.model_api import *


class ct_tfa_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut TFA payment standard"
    definition_period = MONTH
    defined_for = StateCode.CT
    unit = USD
    documentation = (
        "The maximum monthly TFA benefit amount for the household based on "
        "region and household size, before applying income reductions or "
        "family cap adjustments."
    )
    reference = (
        "SSA POMS SI BOS00830.403 - TANF - Connecticut, Benefit Rate Charts; "
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0500830403BOS"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.tfa.payment_standard
        region = spm_unit("ct_tfa_region_str", period.this_year)
        size = spm_unit("ct_tfa_assistance_unit_size", period.this_year)

        # Determine which region parameter to use
        region_a = region == "A"
        region_b = region == "B"
        region_c = region == "C"

        # Get payment standard for each region, capped at max household size
        # The parameter file defines payment standards up to household size 20
        capped_size = min_(size, 20)

        # Convert size to string to match parameter file structure
        size_str = capped_size.astype(str)

        payment_a = p.region_a[size_str]
        payment_b = p.region_b[size_str]
        payment_c = p.region_c[size_str]

        # Return appropriate payment based on region
        return where(
            region_a,
            payment_a,
            where(region_b, payment_b, payment_c),
        )
