from policyengine_us.model_api import *


class ma_connector_care_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Massachusetts ConnectorCare"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://www.mahealthconnector.org/wp-content/uploads/amended-956CMR12.00.pdf#page=5",
        "https://www.mahealthconnector.org/wp-content/uploads/amended-956CMR12.00.pdf#page=6",
        "https://www.mahealthconnector.org/wp-content/uploads/ConnectorCare-Overview-2026.pdf#page=1",
        "https://www.mahealthconnector.org/wp-content/uploads/ConnectorCare-Overview-2026.pdf#page=2",
    )
    documentation = (
        "A tax unit is eligible for ConnectorCare when the program is in "
        "effect, household income (ACA MAGI per 26 U.S.C. 36B(d)(2)) as a "
        "share of the federal poverty line is at or above the 100% FPL floor "
        "and at or below the 400% FPL limit (the operational 2026 band), and "
        "at least one member is eligible for the federal ACA premium tax "
        "credit. Massachusetts residency is enforced by defined_for. The "
        "amended 956 CMR still defines a sub-100% Plan Type 1 and a 400.1-500% "
        "Plan Type 3D, but the 2026 ConnectorCare Overview runs Plan Types "
        "2A-3C only (100-400% FPL), and that operational reading is treated as "
        "controlling."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ma.hic.connector_care
        in_effect = p.in_effect
        magi_fraction = tax_unit("aca_magi_fraction", period)
        income_eligible = (magi_fraction >= p.fpl_floor) & (
            magi_fraction <= p.fpl_limit
        )
        has_eligible_member = (
            add(tax_unit, period, ["ma_connector_care_member_eligible"]) > 0
        )
        return in_effect & income_eligible & has_eligible_member
