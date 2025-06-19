from policyengine_us.model_api import *
from policyengine_core.periods import instant


class ny_ctc_pre_2024_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "NY CTC pre-2024 eligibility"
    documentation = (
        "Whether the tax unit is eligible for NY CTC under pre-2024 rules"
    )
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (c-1)
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.credits.ctc

        # Only eligible if post-2024 rules are NOT in effect
        if p.post_2024.in_effect:
            return False

        person = tax_unit.members
        age = person("age", period)

        # Check if we have qualifying children
        if not p.pre_tcja:
            qualifies_for_federal_ctc = person("ctc_qualifying_child", period)
        else:
            # Initialize pre-TCJA CTC branch for eligibility check
            simulation = tax_unit.simulation
            pre_tcja_ctc = simulation.get_branch("pre_tcja_ctc")
            pre_tcja_ctc.tax_benefit_system = (
                simulation.tax_benefit_system.clone()
            )
            branch_parameters = pre_tcja_ctc.tax_benefit_system.parameters
            # Update parameters to pre-TCJA values.
            for (
                ctc_parameter
            ) in branch_parameters.gov.irs.credits.ctc.get_descendants():
                if isinstance(ctc_parameter, Parameter):
                    ctc_parameter.update(
                        start=instant("2017-01-01"),
                        stop=instant("2026-01-01"),
                        value=ctc_parameter("2017-01-01"),
                    )
            # Delete all arrays from pre-TCJA CTC branch.
            for variable in pre_tcja_ctc.tax_benefit_system.variables:
                if "ctc" in variable:
                    pre_tcja_ctc.delete_arrays(variable)
            qualifies_for_federal_ctc = pre_tcja_ctc.person(
                "ctc_qualifying_child", period
            )

        qualifies = qualifies_for_federal_ctc & (age >= p.minimum_age)
        qualifying_children = tax_unit.sum(qualifies)
        return qualifying_children > 0
