from policyengine_us.model_api import *


class unemployment_compensation_months(Variable):
    value_type = int
    entity = Person
    label = "Months with unemployment compensation receipt"
    unit = "month"
    definition_period = YEAR
    documentation = (
        "Number of calendar months in the year in which the person receives "
        "unemployment compensation, for the SNAP work registration exemption "
        "of a person receiving unemployment compensation (7 CFR "
        "273.7(b)(1)(v)). Weeks unemployed are converted to months as "
        "ceil(weeks x 12 / 52), capped at 12. weeks_unemployed is weeks "
        "spent looking for work (CPS ASEC LKWEEKS); for a recipient it "
        "includes the waiting week and any weeks after benefits run out, "
        "so it bounds the weeks paid from above. When unemployment "
        "compensation is positive but weeks_unemployed is 0 (not reported, "
        "as on ACS-based rows until PolicyEngine/microcosm#1022, or a "
        "recipient on temporary layoff who was not looking for work), the "
        "receipt is treated as lasting all 12 months, which was the "
        "model's behavior before months of receipt were modeled."
    )
    reference = "https://www.law.cornell.edu/cfr/text/7/273.7#b_1_v"

    def formula(person, period, parameters):
        # Reported unemployment compensation, or modeled state unemployment
        # insurance when none is reported.
        receives = person("total_unemployment_compensation", period) > 0
        weeks = person("weeks_unemployed", period)
        # NOTE: multiplying before dividing keeps whole weeks exact, so 13
        # weeks gives exactly 3 months before rounding up.
        months_from_weeks = np.ceil(
            clip(weeks, 0, WEEKS_IN_YEAR) * MONTHS_IN_YEAR / WEEKS_IN_YEAR
        )
        months = where(weeks > 0, months_from_weeks, MONTHS_IN_YEAR)
        return where(receives, months, 0).astype(int)
