from policyengine_us.model_api import *


class ct_temporary_premium_assistance(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut Temporary Premium Assistance"
    unit = USD
    definition_period = YEAR
    defined_for = "ct_temporary_premium_assistance_eligible"
    reference = (
        "https://www.accesshealthct.com/article/active/new-financial-help-could-lower-your-health-coverage-costs-in-2026/",
        "https://www.accesshealthct.com/financial-help/",
        "https://www.accesshealthct.com/federal-changes-to-health-coverage/",
        "https://portal.ct.gov/cid/consumer-information-center/consumer-alerts/2026-consumer-alerts/notice-2026-02-13",
        "https://portal.ct.gov/governor/news/press-releases/2025/12-2025/governor-lamont-submits-plan-to-tap-into-emergency-state-response-reserve",
        # Public Act 26-68, Section 453(a)(8), (b)(2) and (e).
        # PDF pages 691, 693
        "https://www.cga.ct.gov/2026/ACT/PA/PDF/2026PA-00068-R00SB-00001-PA.PDF#page=691",
        "https://portal.ct.gov/governor/news/press-releases/2026/11-2026/governor-lamont-and-insurance-commissioner-hershman-encourage-residents-to-review-health-coverage",
    )
    documentation = (
        "State premium assistance for Access Health CT enrollees in plan "
        "years 2026 and 2027 that replaces some or all of the enhanced "
        "federal premium tax credit that expired at the end of 2025. In the "
        "full replacement band (100% to 200% of the poverty line, outside "
        "Covered Connecticut) it pays the enhanced credit less the current "
        "federal credit, so the enrollee gets 'the same amount you would "
        "have if the federal tax credits had not expired'. In the partial "
        "replacement band (above 400% and up to 500%), where the current "
        "federal credit is $0, it pays half of the enhanced credit. Both "
        "bands use the same form: the band's replacement rate times the "
        "enhanced credit less the current credit, floored at zero. The "
        "assistance is paid monthly to the insurer and is not a tax credit, "
        "so it is not reconciled and is not added to taxable income. "
        "Approximations: the benchmark silver plan (aca_ptc_slcsp) stands in "
        "for the enrolled plan in both credits, so the amount is not capped "
        "at a cheaper plan's premium; amounts are annual and assume full-year "
        "enrollment; the 2026 special enrollment window, the plan metal "
        "requirement and recovery of assistance paid to ineligible people "
        "are not modeled."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ct.ahct.temporary_premium_assistance
        ratio = tax_unit("ct_temporary_premium_assistance_fpl_ratio", period)
        # An eligible tax unit is in exactly one band, and the full
        # replacement band ends below the partial band's floor.
        in_full_band = ratio <= p.full_replacement.fpl_limit
        rate = where(in_full_band, p.full_replacement.rate, p.partial_replacement.rate)
        enhanced = tax_unit("ct_temporary_premium_assistance_enhanced_ptc", period)
        current = tax_unit("aca_ptc", period)
        return rate * max_(0, enhanced - current)
