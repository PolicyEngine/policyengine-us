from policyengine_us.model_api import *


class ct_temporary_premium_assistance_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Connecticut Temporary Premium Assistance"
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = (
        "https://www.accesshealthct.com/article/active/new-financial-help-could-lower-your-health-coverage-costs-in-2026/",
        "https://www.accesshealthct.com/financial-help/",
        "https://www.accesshealthct.com/federal-changes-to-health-coverage/",
        "https://help.accesshealthct.com/en_US/premium-assistance",
        "https://portal.ct.gov/cid/consumer-information-center/consumer-alerts/2026-consumer-alerts/notice-2026-02-13",
        # Public Act 26-68, Section 453(e): the plan year 2027 subsidy.
        "https://www.cga.ct.gov/2026/ACT/PA/PDF/2026PA-00068-R00SB-00001-PA.PDF#page=693",
    )
    documentation = (
        "A tax unit qualifies for Temporary Premium Assistance in one of two "
        "income bands, measured on the exact ratio of ACA MAGI to the "
        "premium tax credit poverty line "
        "(ct_temporary_premium_assistance_fpl_ratio). Full replacement: "
        "income from 100% to 200% of the poverty line, at least one member "
        "eligible for the federal premium tax credit, not eligible for the "
        "Covered Connecticut Program ('You cannot be enrolled in the Covered "
        "CT Program and receive TPA'), and filing a return that claims the "
        "federal credit, since Access Health CT requires enrollees to accept "
        "all the advance credit available to them and advance payments must "
        "be reconciled on a return. Partial replacement: income above 400% "
        "and up to 500% of the poverty line, and at least one member who "
        "would be eligible for the federal credit but for its 400% income "
        "cap, that is, a Marketplace enrollee who pays a premium "
        "(pays_aca_premium, which carries the 2027 immigration limits), is "
        "in the premium tax credit tax family and is not on a separate "
        "return. No federal credit exists above 400%, so there is no advance "
        "credit to accept and no filing condition in that band. Nothing is "
        "paid between 200% and 400%. Not modeled: the Bronze, Silver or Gold "
        "plan requirement (catastrophic plans are excluded) and the request "
        "for financial help on the application."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ct.ahct.temporary_premium_assistance
        ratio = tax_unit("ct_temporary_premium_assistance_fpl_ratio", period)
        person = tax_unit.members

        # Full replacement band: "between 100% and 200%", with Access Health
        # CT's dollar range inclusive at both ends.
        in_full_band = (ratio >= p.full_replacement.fpl_floor) & (
            ratio <= p.full_replacement.fpl_limit
        )
        ptc_eligible = tax_unit.any(person("is_aca_ptc_eligible", period))
        # Covered Connecticut already pays the premium left after the
        # federal credit, and its enrollees cannot receive this assistance.
        in_covered_ct = tax_unit("ct_covered_connecticut_eligible", period)
        # Accepting all available advance credit means filing to reconcile
        # it (26 CFR 1.6011-8(a)).
        files = tax_unit("files_return_for_aca_ptc", period)
        full = in_full_band & ptc_eligible & ~in_covered_ct & files

        # Partial replacement band: "over 400% and up to 500%", from
        # "$62,600.01" for one person in plan year 2026.
        in_partial_band = (ratio > p.partial_replacement.fpl_floor) & (
            ratio <= p.partial_replacement.fpl_limit
        )
        # is_aca_ptc_eligible is false above 400% from 2026, so test the
        # federal conditions other than income: Marketplace enrollment with
        # a premium (TIN, immigration status, no other minimum essential
        # coverage) and membership in the tax family.
        enrollee = person("pays_aca_premium", period) & person(
            "is_aca_tax_family_member", period
        )
        filing_status = tax_unit("filing_status", period)
        not_separate = filing_status != filing_status.possible_values.SEPARATE
        partial = in_partial_band & tax_unit.any(enrollee) & not_separate

        return p.in_effect & (full | partial)
