from policyengine_us.model_api import *
from policyengine_core.simulations import Simulation

def get_ca_eitc_branch(tax_unit, period, parameters):
    simulation: Simulation = tax_unit.simulation
    if "ca_eitc" not in simulation.branches:
        branch = simulation.get_branch("ca_eitc")
        branch.tax_benefit_system = branch.tax_benefit_system.clone()

        # Change parameters.

        VARIABLES_TO_CLEAR = [
            "eitc_eligible",
            "eitc_phase_in_rate",
            "eitc_phase_out_rate",
            "eitc_maximum",
            "eitc_phased_in",
            "eitc_reduction",
        ]

        for variable in VARIABLES_TO_CLEAR:
            branch.delete_arrays(variable)

        # Change parameters

        def modify_parameters(parameters: ParameterNode) -> ParameterNode:
            eitc = parameters.gov.irs.credits.eitc
            ca_eitc = parameters.gov.states.ca.tax.income.credits.earned_income
            current_ca_eitc = ca_eitc(period)

            # Age expansion
            eitc.eligibility.age.max.update(
                period=period, value=current_ca_eitc.eligibility.age.max
            )
            eitc.eligibility.age.min.update(
                period=period, value=current_ca_eitc.eligibility.age.min
            )

            # Investment income change
            eitc.phase_out.max_investment_income.update(
                period=period, value=current_ca_eitc.eligibility.max_investment_income
            )

            # EITC amount and phase-out amount changes
            for i in range(len(eitc.max.brackets)):
                ca_i = min(
                    i, len(ca_eitc.earned_income_amount.brackets) - 1
                )  # Federal policy having more brackets => use the top of CA's policy
                for attribute in ["amount"]:
                    # Federal EITCs are specified in terms of the maximum amount, but
                    # CA EITC parameters are in terms of the maximum earned income amount,
                    # so we need to multiply the CA parameter by the relevant phase-in rate.
                    # Phase-in rate
                    phase_in_rate = eitc.phase_in_rate.brackets[i].amount(period)
                    eitc_max_amount = getattr(
                        ca_eitc.earned_income_amount.brackets[ca_i],
                        attribute,
                    )(period) * (phase_in_rate if attribute == "amount" else 1)
                    getattr(eitc.max.brackets[i], attribute).update(
                        period=period,
                        value=eitc_max_amount,
                    )
                    # Phase-out start
                    getattr(
                        eitc.phase_out.start.brackets[i], attribute
                    ).update(
                        period=period,
                        value=getattr(
                            ca_eitc.phase_out.start.brackets[ca_i], attribute
                        )(period)
                    )
                    # Phase-out rate
                    getattr(
                        eitc.phase_out.rate.brackets[i], attribute
                    ).update(
                        period=period,
                        value=getattr(
                            ca_eitc.phase_out.rate.brackets[i], attribute
                        )(period)
                    )
        branch.tax_benefit_system.modify_parameters(modify_parameters)
        return branch
    else:
        return simulation.branches.get("ca_eitc")

class ca_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "CalEITC amount"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/file/personal/credits/california-earned-income-tax-credit.html#What-you-ll-get"

    def formula(tax_unit, period, parameters):
        branch = get_ca_eitc_branch(tax_unit, period, parameters)
        ca_eitc = parameters.gov.states.ca.tax.income.credits.earned_income
        current_ca_eitc = ca_eitc(period)
        amount = branch.calculate("earned_income_tax_credit", period) * current_ca_eitc.adjustment.factor
        second_phase_out_start = tax_unit("ca_eitc_second_phase_out_start", period)
        second_phase_out_end = current_ca_eitc.phase_out.final.end
        count_children = tax_unit("eitc_child_count", period)
        eitc_at_second_phase_out_start = current_ca_eitc.phase_out.final.start.calc(count_children)
        earned_income = tax_unit("filer_earned", period)
        amount_along_second_phase_out = (earned_income - second_phase_out_start)
        second_phase_out_width = second_phase_out_end - second_phase_out_start
        percent_along_second_phase_out = amount_along_second_phase_out / second_phase_out_width
        eitc_along_second_phase_out = max_((
            eitc_at_second_phase_out_start
        ) * (1 - percent_along_second_phase_out), 0)

        is_on_second_phase_out = (
            (earned_income >= second_phase_out_start)
        )

        return where(
            is_on_second_phase_out,
            eitc_along_second_phase_out,
            amount,
        )


class ca_eitc_second_phase_out_start(Variable):
    value_type = float
    entity = TaxUnit
    label = "CalEITC second phase-out start"
    unit = USD
    documentation = "California begins secondarily phasing out the CalEITC at this earnings level."
    definition_period = YEAR


    def formula(tax_unit, period, parameters):
        maximum = tax_unit("ca_eitc_maximum", period)
        ca_eitc = parameters(period).gov.states.ca.tax.income.credits.earned_income
        count_children = tax_unit("eitc_child_count", period)
        # Apply the adjustment factor to the phase-out rate.
        phase_out_rate = ca_eitc.phase_out.rate.calc(count_children) * ca_eitc.adjustment.factor
        # Multiply and divide the second phase-out start by the adjustment factors.
        eitc_at_which_second_phase_out_starts = ca_eitc.phase_out.final.start.calc(count_children) * ca_eitc.adjustment.factor / ca_eitc.adjustment.divisor
        eitc_difference = maximum - eitc_at_which_second_phase_out_starts
        earnings_to_cover_eitc_difference = eitc_difference / phase_out_rate
        return earnings_to_cover_eitc_difference + ca_eitc.phase_out.start.calc(count_children)
    

class ca_eitc_maximum(Variable):
    value_type = float
    entity = TaxUnit
    label = "CalEITC maximum"
    unit = USD
    documentation = "California provides an earned income tax credit up to this value, based on the earned income amounts and phase-in rates, which vary with number of qualifying children."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        branch = get_ca_eitc_branch(tax_unit, period, parameters)
        adjustment = parameters(period).gov.states.ca.tax.income.credits.earned_income.adjustment.factor
        return branch.calculate("eitc_maximum", period) * adjustment