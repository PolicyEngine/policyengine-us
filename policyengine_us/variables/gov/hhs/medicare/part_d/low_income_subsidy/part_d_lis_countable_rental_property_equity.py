from policyengine_us.model_api import *


class part_d_lis_countable_rental_property_equity(Variable):
    value_type = float
    entity = Household
    label = (
        "Countable rental property equity for the Medicare Part D low-income subsidy"
    )
    documentation = (
        "Equity in rental property counts as a resource, less the exclusion "
        "for income-producing property essential to self-support: up to the "
        "equity exclusion when the household's net rental income is at least "
        "the minimum return on the excluded equity. If the return falls "
        "short, all of the equity counts."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1395w-114#a_3_E_i",
        "https://www.law.cornell.edu/uscode/text/42/1382b#a_3",
        "https://www.ecfr.gov/current/title-20/chapter-III/part-418/subpart-D/section-418.3405#p-418.3405(b)",
        "https://www.ecfr.gov/current/title-20/chapter-III/part-416/subpart-L/section-416.1222#p-416.1222(a)",
        "https://secure.ssa.gov/poms.nsf/lnx/0603030020",
        "https://secure.ssa.gov/poms.nsf/lnx/0501130503",
    )

    def formula(household, period, parameters):
        p = parameters(
            period
        ).gov.hhs.medicare.part_d.low_income_subsidy.eligibility.resources.rental_property
        # SSA applies the SSI exclusions to Extra Help (POMS HI 03030.020),
        # including the one for nonbusiness income-producing property (SI
        # 01130.503), which covers a rental reported on Schedule E. Rental
        # property used in a trade or business is excluded regardless of
        # value (SI 01130.501), but the model can't tell the two apart and
        # treats every rental as nonbusiness. It also treats the household's
        # rentals as one property and does not model the exception for a
        # temporary shortfall beyond the owner's control.
        equity = max_(household("household_rental_property_equity", period), 0)
        net_rental_income = add(household, period, ["rental_income"])
        excludable = min_(equity, p.equity_exclusion)
        meets_return = net_rental_income >= p.minimum_return * excludable
        return equity - where(meets_return, excludable, 0)
