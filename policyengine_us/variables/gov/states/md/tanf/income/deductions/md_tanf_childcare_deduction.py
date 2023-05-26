from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.md.tanf.md_tanf_count_children import (
    md_tanf_count_children,
)


class md_tanf_childcare_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF childcare deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD

    def formula(spm_unit, period, parameters):
        workhours = add(spm_unit, period, ["workhour"])

        # Get the policy parameters.
        p = parameters(
            period
        ).gov.states.md.tanf.income.deductions.earnings_exclusion
        childcare_deduction = (
            200 * (workhours >= 100) * md_tanf_count_children
            + 100 * (workhours < 100) * md_tanf_count_children
        )

        # Return if initially eligible
        return childcare_deduction
