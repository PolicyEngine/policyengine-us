from policyengine_us.model_api import *


class ga_ctc_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for the Georgia Child Tax Credit"
    definition_period = YEAR
    defined_for = StateCode.GA
    reference = (
        "https://gov.georgia.gov/document/2025-signed-legislation/hb-136/download#page=3",
        # IRC 24(c).
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title26/html/USCODE-2024-title26-subtitleA-chap1-subchapA-partIV-subpartA-sec24.htm",
        # Georgia Department of Revenue, Qualifying Child Credit (tax years
        # beginning on or after January 1, 2026).
        "https://dor.georgia.gov/qualifying-child-credit",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ga.tax.income.credits.ctc
        age = person("age", period)
        # Georgia lawmakers adopted IRC 24(c) in O.C.G.A. 48-7-29.27, without
        # 24(a)'s dependent deduction condition or 24(h)(7)'s SSN requirement.
        # Under 24(c)(2), a child must remain a dependent after narrowing
        # 152(b)(3)(A)'s citizenship condition. A dependent taxpayer has no
        # dependents under 152(b)(1); apply the claimant filing exception
        # before testing either filer.
        p_federal = parameters(period).gov.irs.credits.ctc
        ctc_eligible_child = person("is_tax_unit_dependent", period) & (
            age < p_federal.amount.base.thresholds[-1]
        )
        filer_is_dependent = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        return ctc_eligible_child & (age < p.age_threshold) & ~filer_is_dependent
