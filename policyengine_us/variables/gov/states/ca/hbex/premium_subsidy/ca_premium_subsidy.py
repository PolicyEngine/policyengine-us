from policyengine_us.model_api import *


class ca_premium_subsidy(Variable):
    value_type = float
    entity = TaxUnit
    label = "California Premium Subsidy"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        "https://board.coveredca.com/meetings/2025/July%2028,%202025/CoveredCA_2026_Premium_Subsidy_Program_Design_Final.pdf#page=1",
        "https://leginfo.legislature.ca.gov/faces/codes_displayText.xhtml?lawCode=GOV&division=&title=25.&part=&chapter=&article=",
    )
    documentation = (
        "California state advance premium assistance subsidy topping up the "
        "federal ACA premium tax credit. It reduces the enrollee's required "
        "contribution toward the benchmark second lowest cost silver plan from "
        "the federal residual to the lower California applicable percentage, "
        "net of the federal advance premium tax credit, floored at zero. The "
        "statutory cap at the enrolled-plan premiums is approximated by the "
        "benchmark SLCSP residual, matching the federal PTC and New Mexico "
        "conventions. FTB reconciliation, repayment caps, the annual "
        "appropriation cap, and advance-payment mechanics are not modeled."
    )

    def formula(tax_unit, period, parameters):
        # Clamp income to zero so a negative ACA MAGI cannot inflate the top-up
        # above the benchmark - APTC residual via the -pct*income term.
        income = max_(tax_unit("aca_magi", period), 0)
        # slcsp is a MONTH-period variable; core sums the 12 months when
        # called from this YEAR formula.
        slcsp = add(tax_unit, period, ["slcsp"])
        aca_ptc = tax_unit("aca_ptc", period)
        ca_pct = tax_unit("ca_premium_subsidy_applicable_percentage", period)
        amount = max_(0, slcsp - aca_ptc - ca_pct * income)
        eligible = tax_unit("ca_premium_subsidy_eligible", period)
        return where(eligible, amount, 0)
