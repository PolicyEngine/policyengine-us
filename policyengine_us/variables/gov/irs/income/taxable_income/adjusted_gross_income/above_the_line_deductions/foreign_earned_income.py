from policyengine_us.model_api import *
from policyengine_core.parameters import get_parameter
from policyengine_core.simulations.simulation import _uprating_index_value
from policyengine_us.tools.default_uprating import DEFAULT_DOLLAR_INPUT_UPRATING


class foreign_earned_income_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Foreign earned income exclusion"
    unit = USD
    documentation = "Income earned and any housing expense in foreign countries that is excluded from adjusted gross income under 26 U.S. Code § 911. Other income inputs are the amounts left after the exclusion. Section 911(f) adds this amount back to set the tax rates on that income: line 2c of the Foreign Earned Income Tax Worksheet (Form 2555 lines 45 and 50, less deductions disallowed because they relate to the excluded income). Modified adjusted gross incomes add back section_911_excluded_income, the Form 2555 amounts before that subtraction. The net investment income tax adds back only the section 911(a)(1) part; see niit_magi_section_911_addition. When not entered directly, it is derived as Form 2555 line 43 minus line 44, plus line 50, minus worksheet line 2b, floored at zero. An entered legacy amount, including zero, overrides that calculation. Without supplied leaf inputs, the legacy default, carry-over, and uprating behavior are preserved."
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/911",
        "https://www.irs.gov/pub/irs-pdf/i1040gi.pdf#page=37",
    ]

    def formula(tax_unit, period, parameters):
        leaf_inputs = [
            "foreign_earned_income_exclusion_amount",
            "foreign_housing_exclusion",
            "foreign_earned_income_exclusion_allocable_deductions",
            "foreign_housing_deduction",
            "foreign_earned_income_exclusion_disallowed_deductions",
        ]
        if not any(
            input_period.start <= period.start
            for variable in leaf_inputs
            for input_period in tax_unit.simulation._get_exportable_input_periods(
                variable, include_computed_variables=False
            )
        ):
            # A formula cannot also declare Core uprating. Preserve the
            # old dollar input's per-capita default uprating here instead,
            # including signed inputs and Core's held-flat index boundaries.
            simulation = tax_unit.simulation
            holder = simulation.get_holder("foreign_earned_income_exclusion")
            earlier_periods = [
                known_period
                for known_period in holder.get_known_periods()
                if known_period.unit == period.unit
                and known_period.start < period.start
            ]
            if not earlier_periods:
                return None
            latest = max(earlier_periods, key=lambda known_period: known_period.start)
            index = get_parameter(
                simulation.tax_benefit_system.parameters,
                DEFAULT_DOLLAR_INPUT_UPRATING + "_per_capita",
            )
            before = _uprating_index_value(index, latest.start)
            after = _uprating_index_value(index, period.start)
            factor = (
                1 if before is None or after is None or before == 0 else after / before
            )
            return holder.get_array(latest, simulation.branch_name) * factor
        gross = tax_unit("foreign_earned_income_exclusion_gross", period)
        allocable_deductions = tax_unit(
            "foreign_earned_income_exclusion_allocable_deductions", period
        )
        housing_deduction = tax_unit("foreign_housing_deduction", period)
        disallowed_deductions = tax_unit(
            "foreign_earned_income_exclusion_disallowed_deductions", period
        )
        # Worksheet line 2c: if zero or less, enter zero. Other income and
        # deduction inputs retain their existing model definitions.
        return max_(
            0, gross - allocable_deductions + housing_deduction - disallowed_deductions
        )
