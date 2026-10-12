from policyengine_us.model_api import *


class nj_njhps_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for New Jersey Health Plan Savings"
    definition_period = YEAR
    defined_for = StateCode.NJ
    reference = (
        "https://www.cms.gov/files/document/1332-ota-methodology-addendum-nj-pass-through.pdf#page=8",
        "https://pub.njleg.gov/bills/2020/AL20/61_.HTM",
    )
    documentation = (
        "A tax unit is eligible for New Jersey Health Plan Savings when the "
        "program is in effect, household income (ACA MAGI per 26 U.S.C. "
        "36B(d)(2)) is at least 138% and at most 600% of the federal poverty "
        "line, and at least one member is an NJHPS enrollee. Households below "
        "138% FPL are routed to NJ FamilyCare/Medicaid rather than NJHPS; the "
        "138% floor is inclusive and the 600% ceiling is inclusive. New Jersey "
        "residency is enforced by defined_for."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nj.dobi.njhps
        in_effect = p.in_effect
        magi_fraction = tax_unit("aca_magi_fraction", period)
        income_eligible = (magi_fraction >= p.fpl_floor) & (
            magi_fraction <= p.fpl_limit
        )
        has_eligible_member = add(tax_unit, period, ["nj_njhps_member_eligible"]) > 0
        return in_effect & income_eligible & has_eligible_member
