from policyengine_us.model_api import *


class ri_works_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Rhode Island Works countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/rhode-island/218-RICR-20-00-2.15",
        "https://rules.sos.ri.gov/Regulations/part/218-20-00-2",
    )
    defined_for = StateCode.RI

    def formula(spm_unit, period, parameters):
        # Per 218-RICR-20-00-2.15: First $50 of child support excluded
        p = parameters(period).gov.states.ri.dhs.works.income
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        # Child support is included in gross unearned; apply $50 exclusion
        # Note: child_support_received is YEAR-defined but when accessed in
        # a MONTH period context, automatic period conversion divides by 12
        child_support = add(spm_unit, period, ["child_support_received"])
        child_support_exclusion = min_(
            child_support, p.child_support_disregard
        )
        return max_(gross_unearned - child_support_exclusion, 0)
