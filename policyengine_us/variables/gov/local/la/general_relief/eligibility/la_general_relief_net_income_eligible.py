from policyengine_us.model_api import *


class la_general_relief_net_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Los Angeles County General Relief based on the net income requirements"
    definition_period = MONTH
    # Person has to be a resident of LA County
    defined_for = "in_la"
    reference = "https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing"

    def formula(spm_unit, period, parameters):
        pre_deductions_net_income = add(
            spm_unit, period, ["la_general_relief_net_income"]
        )
        state_deductions = add(spm_unit, period, ["ca_deductions"])
        federal_deductions = add(
            spm_unit, period, ["taxable_income_deductions"]
        )
        post_deductions_net_income = max_(
            pre_deductions_net_income - state_deductions - federal_deductions,
            0,
        )
        p = parameters(
            period
        ).gov.local.la.general_relief.eligibility.limit.income
        married = add(spm_unit, period, ["is_married"])
        return where(
            married,
            post_deductions_net_income <= p.married,
            post_deductions_net_income <= p.single,
        )
