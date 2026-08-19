from policyengine_us.model_api import *


class ny_ui(Variable):
    """Annual New York State unemployment insurance benefit. Implements the
    monetary eligibility tests, weekly benefit rate, partial-benefit
    calculation, and benefit duration from NY Labor Law Article 18 (§§ 500-641).

    Not modeled: § 527(2) alternate base period; § 527(6) requalification after
    a prior benefit year; § 600 pension / retirement-pay offset; § 591
    availability, capability, and active-work-search requirements; § 590(4)
    duration exceptions cross-referencing § 601 and § 599(2). New York has NO
    dependency allowance.
    """

    value_type = float
    entity = Person
    label = "New York unemployment insurance"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/LAB/590"
    defined_for = "ny_ui_monetarily_eligible"

    def formula(person, period, parameters):
        # ny_ui is deliberately not yet wired into any income aggregate; any
        # eventual wiring must not double-count with unemployment_compensation.
        p = parameters(period).gov.states.ny.dol.unemployment_insurance.benefit
        weekly_benefit_rate = person("ny_ui_weekly_benefit_rate", period)
        weekly_payable = person("ny_ui_weekly_payable", period)
        # Floor weeks at zero so a negative input cannot produce a negative
        # benefit (mirrors the AL/OK UI guard pattern).
        weeks_unemployed = max_(person("weeks_unemployed", period), 0)

        # Maximum benefit amount caps total benefits at the weekly rate times
        # the maximum benefit weeks within the benefit year (§ 590).
        maximum_benefit_amount = weekly_benefit_rate * p.max_weeks
        annual_benefit = weekly_payable * weeks_unemployed
        return min_(annual_benefit, maximum_benefit_amount)
