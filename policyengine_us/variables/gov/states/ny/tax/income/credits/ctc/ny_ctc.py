from policyengine_us.model_api import *
from policyengine_core.periods import instant


class ny_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY CTC"
    documentation = "New York's Empire State Child Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (c-1)
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.credits.ctc
        person = tax_unit.members
        age = person("age", period)
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)

        # Check if updated CTC rules apply (2025-2027)
        try:
            updated_ctc_applies = (p.updated.young_child_amount > 0) or (
                p.updated.older_child_amount > 0
            )
        except:
            # If updated parameters don't exist, use original logic
            updated_ctc_applies = False

        if updated_ctc_applies:
            # Updated CTC rules for 2025-2027
            qualifies_for_federal_ctc = person("ctc_qualifying_child", period)
            qualifies = qualifies_for_federal_ctc & (age >= p.minimum_age)

            # Age-based amounts: 0-3 years old vs 4-16 years old
            young_children = qualifies & (age <= 3)
            older_children = qualifies & (age >= 4) & (age <= 16)

            young_child_credit = (
                tax_unit.sum(young_children) * p.updated.young_child_amount
            )
            older_child_credit = (
                tax_unit.sum(older_children) * p.updated.older_child_amount
            )
            base_credit = young_child_credit + older_child_credit

            # Apply phase-out if base credit > 0
            if p.updated.phase_out_rate > 0:
                filing_statuses = filing_status.possible_values
                phase_out_threshold = select(
                    [
                        filing_status == filing_statuses.SINGLE,
                        filing_status == filing_statuses.JOINT,
                        filing_status == filing_statuses.HEAD_OF_HOUSEHOLD,
                        filing_status == filing_statuses.SEPARATE,
                        filing_status == filing_statuses.SURVIVING_SPOUSE,
                    ],
                    [
                        p.updated.phase_out_threshold.single,
                        p.updated.phase_out_threshold.joint,
                        p.updated.phase_out_threshold.head_of_household,
                        p.updated.phase_out_threshold.separate,
                        p.updated.phase_out_threshold.surviving_spouse,
                    ],
                )
                excess_income = max_(agi - phase_out_threshold, 0)
                # Round up to nearest $1,000 for phase-out calculation
                excess_thousands = (excess_income + 999) // 1000
                phase_out_amount = (
                    excess_thousands * p.updated.phase_out_rate * 1000
                )
                return max_(base_credit - phase_out_amount, 0)
            else:
                return base_credit

        else:
            # Original CTC rules (pre-2025 and post-2027)
            if not p.pre_tcja:
                federal_ctc = tax_unit("ctc", period)
                gov = parameters(period).gov
                qualifies_for_federal_ctc = person(
                    "ctc_qualifying_child", period
                )
            else:
                # Initialise pre-TCJA CTC branch and parameters.
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
            eligible = qualifying_children > 0
            return eligible * max_(applicable_minimum, federal_match)
