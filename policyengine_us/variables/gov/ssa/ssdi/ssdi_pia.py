from policyengine_us.model_api import *


class ssdi_pia(Variable):
    value_type = float
    entity = Person
    label = "SSDI Primary Insurance Amount (PIA)"
    unit = USD
    definition_period = MONTH
    reference = "https://www.ssa.gov/oact/cola/piaformula.html"
    documentation = """
    Primary Insurance Amount for SSDI, calculated using the three-tier progressive formula
    based on Average Indexed Monthly Earnings (AIME).
    """

    def formula(person, period, parameters):
        p = parameters(period).gov.ssa.ssdi.pia

        aime = person("ssdi_aime", period.this_year)
        monthly_aime = aime / 12  # Convert annual to monthly

        # First bend point calculation
        first_portion = min_(monthly_aime, p.bend_points.first)
        first_amount = first_portion * p.percentages.first

        # Second bend point calculation
        second_portion = max_(
            0,
            min_(
                monthly_aime - p.bend_points.first,
                p.bend_points.second - p.bend_points.first,
            ),
        )
        second_amount = second_portion * p.percentages.second

        # Third portion (above second bend point)
        third_portion = max_(0, monthly_aime - p.bend_points.second)
        third_amount = third_portion * p.percentages.third

        # Total monthly PIA (rounded down to nearest $0.10)
        monthly_pia = first_amount + second_amount + third_amount
        monthly_pia = np.floor(monthly_pia * 10) / 10

        # Return monthly amount (not annual)
        return monthly_pia
