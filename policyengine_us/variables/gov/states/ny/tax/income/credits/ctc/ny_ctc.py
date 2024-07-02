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
        if not p.pre_tcja:
            federal_ctc = tax_unit("ctc", period)
            gov = parameters(period).gov
            qualifies_for_federal_ctc = person("ctc_qualifying_child", period)
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
            federal_ctc = pre_tcja_ctc.tax_unit("ctc", period)
            qualifies_for_federal_ctc = pre_tcja_ctc.person(
                "ctc_qualifying_child", period
            )
            gov = branch_parameters(period).gov

        # Remaining logic is based on NY parameters (Form IT-213 Step 4)
        # Form IT-213 - Line 6
        # worksheet A line 10 OR worksheet B line 13
        # Form IT-213 - Line 7
        # additional child tax amount
        # Form IT-213 - Line 8 = max_(0, Line 6 + Line 7)
        # Form IT-213 - Line 9
        qualifying_children = tax_unit.sum(qualifies_for_federal_ctc)
        # Form IT-213 - Line 10
        # fraction = line 8/qualifying_children
        # Form IT-213 - Line 11 & Line 14
        qualifies = qualifies_for_federal_ctc & (age >= p.minimum_age)
        qualifying_children_age_limit = tax_unit.sum(qualifies)
        # Form IT-213 - Line 12 = fraction * qualifying_children_age_limit
        # Form IT-213 - Line 13 = line 12 * p.amount.percent
        # Form IT-213 - Line 15
        minimum = p.amount.minimum * qualifying_children_age_limit
        # Form IT-213 - Line 16 = max_(minimum, line 13)
        # return line 16
