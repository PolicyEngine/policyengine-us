from policyengine_us.model_api import *


class me_tanf_earned_income_after_disregard_person(Variable):
    value_type = float
    entity = Person
    label = "Maine TANF earned income after disregard per person"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.mainelegislature.org/legis/statutes/22/title22sec3762.html",
        "https://www.law.cornell.edu/regulations/maine/10-144-C-M-R-ch-331",
    )
    defined_for = StateCode.ME

    def formula(person, period, parameters):
        # Per 22 M.R.S. Section 3762(3)(B)(7-D)(c):
        # Each individual who is employed is eligible for:
        # i. $108 flat deduction; and
        # ii. 50% disregard of remaining earnings
        # NOTE: First 6 months of employment have higher disregards (100%/75%)
        # that cannot be tracked in PolicyEngine
        p = parameters(period).gov.states.me.dhhs.tanf.earned_income

        gross_earned = person("tanf_gross_earned_income", period)

        # Apply flat deduction first
        after_flat = max_(gross_earned - p.flat_deduction, 0)

        # Apply percentage disregard (50% excluded = 50% counted)
        return after_flat * (1 - p.percentage_disregard)
