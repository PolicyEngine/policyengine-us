from policyengine_us.model_api import *


class vt_reach_up_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Vermont Reach Up dependent care deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/vermont/13-220-Code-Vt-R-13-170-220-X",
        # PDF pages 71, 74-75
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2200-Reach-Up.pdf#page=71",
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/ESD-Procedure-P2230A.pdf",
    )
    defined_for = StateCode.VT

    def formula(spm_unit, period, parameters):
        # Per Section 2252.2(c): $175/month max per participant claiming the deduction.
        # We approximate "participant" as head or spouse since they are the earners.
        # Per Section 2252.2(a), the deduction covers care of a household
        # member who is a disabled or seriously ill adult. Section 2252.2(b)
        # covers child care only for a child who is not a member of the
        # Reach Up household, which the model does not track; child care for
        # children in the unit is not deducted (rule 2251.1(e): child care
        # provided as a Reach Up support service is not a dependent care
        # expense; ESD Procedure P-2230A).
        p = parameters(period).gov.states.vt.dcf.reach_up.income.deductions
        person = spm_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        num_participants = spm_unit.sum(head_or_spouse)
        max_deduction = p.dependent_care * num_participants
        adult_care_expenses = add(spm_unit, period, ["care_expenses"])
        return min_(adult_care_expenses, max_deduction)
