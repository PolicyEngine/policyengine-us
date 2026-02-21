from policyengine_us.model_api import *


class ssdi_engaged_in_sga(Variable):
    value_type = bool
    entity = Person
    label = "Engaged in Substantial Gainful Activity for SSDI"
    definition_period = YEAR
    reference = "https://www.ssa.gov/oact/cola/sga.html"
    documentation = """
    Determines if a person is engaged in Substantial Gainful Activity (SGA).
    If earning above SGA threshold, generally cannot be considered disabled for SSDI.
    """

    def formula(person, period, parameters):
        p = parameters(period).gov.ssa.ssdi.sga

        # Get monthly earnings
        annual_earnings = person("earned_income", period)
        monthly_earnings = annual_earnings / 12

        is_blind = person("is_blind", period)

        # Different thresholds for blind vs non-blind
        sga_threshold = where(is_blind, p.blind, p.non_blind)

        return monthly_earnings > sga_threshold
