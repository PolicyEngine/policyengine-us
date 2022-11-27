from policyengine_us.model_api import *
from policyengine_core.periods import instant
import warnings

warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")


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
        else:
            # Initialise pre-TCJA CTC branch

            simulation = tax_unit.simulation
            pre_tcja_ctc = simulation.get_branch("pre_tcja_ctc")
            pre_tcja_ctc.tax_benefit_system = (
                simulation.tax_benefit_system.clone()
            )

            branch_parameters = pre_tcja_ctc.tax_benefit_system.parameters

            for (
                ctc_parameter
            ) in branch_parameters.gov.irs.credits.ctc.get_descendants():
                if isinstance(ctc_parameter, Parameter):
                    ctc_parameter.update(
                        start=instant("2017-01-01"),
                        stop=instant("2026-01-01"),
                        value=ctc_parameter("2017-01-01"),
                    )

            for variable in pre_tcja_ctc.tax_benefit_system.variables:
                if "ctc" in variable:
                    pre_tcja_ctc.delete_arrays(variable)

            maximum_ctc = pre_tcja_ctc.calculate(
                "ctc_child_individual_maximum", period
            )
            meets_ny_minimum_age = age >= p.minimum_age
            pre_tcja_ctc.set_input(
                "ctc_individual_maximum",
                period,
                maximum_ctc * meets_ny_minimum_age,
            )
            federal_ctc = pre_tcja_ctc.tax_unit("ctc_value", period)

        qualifies_for_federal_ctc = person("ctc_qualifying_child", period)
        qualifies = qualifies_for_federal_ctc & (age >= p.minimum_age)
        qualifying_children = tax_unit.sum(qualifies)
        federal_match = federal_ctc * p.amount.percent
        # Filers with income below the CTC phase-out threshold receive a
        # minimum amount per child.
        minimum = p.amount.minimum * qualifying_children
        agi = tax_unit("adjusted_gross_income", period)
        # Uses pre-TCJA parameters.
        pre_tcja_ctc = parameters("2017-01-01").gov.irs.credits.ctc
        filing_status = tax_unit("filing_status", period)
        federal_threshold = pre_tcja_ctc.phase_out.threshold[filing_status]
        eligible_for_minimum = agi < federal_threshold
        applicable_minimum = eligible_for_minimum * minimum
        eligible = qualifying_children > 0
        return eligible * max_(applicable_minimum, federal_match)
