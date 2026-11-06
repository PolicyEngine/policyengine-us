from policyengine_us.model_api import *


class ga_ctc_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for the Georgia Child Tax Credit"
    definition_period = YEAR
    defined_for = StateCode.GA
    reference = (
        "https://gov.georgia.gov/document/2025-signed-legislation/hb-136/download#page=3",
        "https://www.law.cornell.edu/uscode/text/26/24#c",
        # Georgia Department of Revenue, Qualifying Child Credit (tax years
        # beginning on or after January 1, 2026).
        "https://dor.georgia.gov/qualifying-child-credit",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ga.tax.income.credits.ctc
        age = person("age", period)
        # Georgia lawmakers adopted IRC 24(c) in O.C.G.A. 48-7-29.27, without
        # 24(a)'s dependent deduction condition or 24(h)(7)'s SSN requirement.
        # We retain the reading that 24(c)(2) changes only the citizenship
        # condition; a broader reading would import 152(b)(1)'s
        # no-dependents condition.
        p_federal = parameters(period).gov.irs.credits.ctc
        ctc_eligible_child = person("is_tax_unit_dependent", period) & (
            age < p_federal.amount.base.thresholds[-1]
        )
        return ctc_eligible_child & (age < p.age_threshold)
