from policyengine_us.model_api import *


class ri_rimap(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island Marketplace Affordability Program"
    unit = USD
    definition_period = YEAR
    defined_for = "ri_rimap_eligible"
    reference = (
        "https://webserver.rilegislature.gov/statutes/TITLE42/42-157.2/42-157.2-4.htm",
        "https://webserver.rilegislature.gov/statutes/TITLE42/42-157.2/42-157.2-5.htm",
        # PDF pages 1-3: the statutory criteria and the amount rule (pp.1-2)
        # and the Plan Year 2027 Rhode Island Applicable Percentage Table
        # (p.3).
        "https://healthsourceri.com/wp-content/uploads/2027-RIMAP-Final-Parameters.pdf#page=1",
    )
    documentation = (
        "Rhode Island's state premium subsidy for HealthSource RI enrollees, "
        "paid on top of the federal premium tax credit from 2027. It is set "
        "so that the household pays the Rhode Island applicable percentage "
        "of its income for the benchmark second-lowest-cost silver plan: "
        "the benchmark premium for the credit's coverage family, minus the "
        "federal credit, minus the applicable percentage times household "
        "income, floored at zero. Below 150% of the poverty line the "
        "percentage is 0%, so the subsidy covers the whole benchmark premium "
        "left after the federal credit. The parameters also subtract any "
        "other assistance; Rhode Island's parent and caretaker premium "
        "assistance is not modeled, so nothing else is subtracted. The "
        "amount assumes a benchmark-priced plan: HealthSource RI remits it "
        "to the enrollee's insurer, and a plan cheaper than the benchmark is "
        "not modeled. Take-up is applied in assigned_ri_rimap."
    )

    def formula(tax_unit, period, parameters):
        # Clamp income to zero so a negative ACA MAGI cannot raise the
        # subsidy through the percentage-of-income term.
        income = max_(tax_unit("aca_magi", period), 0)
        # The benchmark for the credit's coverage family, a MONTH variable
        # that core sums over the year here, as in the Vermont and
        # California programs.
        slcsp = add(tax_unit, period, ["aca_ptc_slcsp"])
        aca_ptc = tax_unit("aca_ptc", period)
        rate = tax_unit("ri_rimap_applicable_percentage", period)
        # The federal credit is 0 above 400% of the poverty line, so there
        # the subsidy is the benchmark premium above 18% of income.
        return max_(0, slcsp - aca_ptc - rate * income)
