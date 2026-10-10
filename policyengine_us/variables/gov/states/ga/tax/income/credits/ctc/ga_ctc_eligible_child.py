from policyengine_us.model_api import *


class ga_ctc_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for the Georgia Child Tax Credit"
    definition_period = YEAR
    defined_for = StateCode.GA
    reference = (
        "https://legiscan.com/GA/text/HB136/id/3204611/Georgia-2025-HB136-Enrolled.pdf#page=2",
        "https://www.law.cornell.edu/uscode/text/26/24#c",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ga.tax.income.credits.ctc
        age = person("age", period)
        # Georgia gives "qualifying child" the meaning of IRC 24(c) only, so
        # it is not limited to children for whom the federal credit is
        # allowed (IRC 24(a), 152(b)(1)). Whether a filer who can be claimed
        # as a dependent can claim it is not settled; this keeps the IRC
        # 24(c) child test.
        p_federal = parameters(period).gov.irs.credits.ctc
        ctc_eligible_child = (
            person("is_tax_unit_dependent", period)
            & (age < p_federal.amount.base.thresholds[-1])
            & person("meets_ctc_child_identification_requirements", period)
        )
        return ctc_eligible_child & (age < p.age_threshold)
