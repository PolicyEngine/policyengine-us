from policyengine_us.model_api import *
from policyengine_core.periods import instant


class ny_ctc_pre_2024(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY CTC pre-2024 rules"
    documentation = "New York's Empire State Child Credit under pre-2024 rules (original system)"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (c-1)
    defined_for = "ny_ctc_pre_2024_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.credits.ctc
        person = tax_unit.members
        age = person("age", period)
        agi = tax_unit("adjusted_gross_income", period)

        # Original CTC rules (pre-2025 and post-2027)
        if not p.pre_tcja:
            federal_ctc = tax_unit("ctc", period)
            gov = parameters(period).gov
            qualifies_for_federal_ctc = person("ctc_qualifying_child", period)
        else:
            # Initialize pre-TCJA CTC branch and parameters.
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
            # Calculate pre-TCJA CTC.
            maximum_ctc = pre_tcja_ctc.calculate(
                "ctc_child_individual_maximum", period
            )
            meets_ny_minimum_age = age >= p.minimum_age
            pre_tcja_ctc.set_input(
                "ctc_individual_maximum",
                period,
                maximum_ctc * meets_ny_minimum_age,
            )
            max_federal_ctc = pre_tcja_ctc.tax_unit("ctc", period)
            ctc_phase_in = pre_tcja_ctc.tax_unit("ctc_phase_in", period)
            federal_ctc = min_(max_federal_ctc, ctc_phase_in)
            qualifies_for_federal_ctc = pre_tcja_ctc.person(
                "ctc_qualifying_child", period
            )
            gov = branch_parameters(period).gov

        # Remaining logic is based on NY parameters.
        qualifies = qualifies_for_federal_ctc & (age >= p.minimum_age)
        qualifying_children = tax_unit.sum(qualifies)
        federal_match = federal_ctc * p.amount.percent
        # Filers with income below the CTC phase-out threshold receive a
        # minimum amount per child.
        minimum = p.amount.minimum * qualifying_children
        federal_threshold = gov.irs.credits.ctc.phase_out.threshold[
            tax_unit("filing_status", period)
        ]
        eligible_for_minimum = agi < federal_threshold
        applicable_minimum = eligible_for_minimum * minimum
        return max_(applicable_minimum, federal_match)
