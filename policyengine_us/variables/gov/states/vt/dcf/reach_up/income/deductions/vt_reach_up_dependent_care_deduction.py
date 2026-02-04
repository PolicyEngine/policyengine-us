from policyengine_us.model_api import *


class vt_reach_up_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Vermont Reach Up dependent care deduction"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/vermont/13-220-Code-Vt-R-13-170-220-X"
    defined_for = StateCode.VT

    def formula(spm_unit, period, parameters):
        # Per Section 2252.2(c): $175/month max per participant claiming the deduction.
        # We approximate "participant" as head or spouse since they are the earners.
        p = parameters(period).gov.states.vt.dcf.reach_up.income.deductions
        person = spm_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        num_participants = spm_unit.sum(head_or_spouse)
        max_deduction = p.dependent_care * num_participants
        childcare_expenses = spm_unit("childcare_expenses", period)
        return min_(childcare_expenses, max_deduction)
