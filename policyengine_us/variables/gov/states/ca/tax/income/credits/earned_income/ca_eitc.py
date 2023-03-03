from policyengine_us.model_api import *
from policyengine_core.simulations import Simulation


class ca_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "CalEITC amount"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/file/personal/credits/california-earned-income-tax-credit.html#What-you-ll-get"

    def formula(tax_unit, period, parameters):
        simulation: Simulation = tax_unit.simulation
        branch = simulation.get_branch("ca_eitc")
        branch.tax_benefit_system = branch.tax_benefit_system.clone()
        current_ca_eitc = parameters(
            period
        ).gov.states.ca.tax.income.credits.earned_income

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
                period=period, value=current_ca_eitc.max_age
            )
            eitc.eligibility.age.min.update(
                period=period, value=current_ca_eitc.min_age
            )

            # Investment income change
            eitc.phase_out.max_investment_income.update(
                period=period, value=current_ca_eitc.max_investment_income
            )

            # EITC amount and phase-out amount changes
            for i in range(len(eitc.max.brackets)):
                ca_i = min(
                    i, len(ca_eitc.earned_income_amount.brackets) - 1
                )  # Federal policy having more brackets => use the top of CA's policy
                for attribute in ["amount", "threshold"]:
                    getattr(eitc.max.brackets[i], attribute).update(
                        period=period,
                        value=getattr(
                            ca_eitc.earned_income_amount.brackets[ca_i],
                            attribute,
                        )(period),
                    )
                    getattr(
                        eitc.phase_out.start.brackets[i], attribute
                    ).update(
                        period=period,
                        value=getattr(
                            ca_eitc.phase_out_amount.brackets[ca_i], attribute
                        )(period),
                    )

                # Phase-out by $30k -> phase-out rate(i) = (earned_income_rate(i) * earned_income_amount(i)) / (30k - phase_out_start(i))

                earned_income_rate = ca_eitc.phase_in.rate.brackets[
                    ca_i
                ].amount(period)
                earned_income_amount = (
                    current_ca_eitc.earned_income_amount.amounts[ca_i]
                )
                phase_out_start = current_ca_eitc.phase_out_amount.amounts[
                    ca_i
                ]
                phase_out_end = current_ca_eitc.max_earnings
                phase_out_rate = (
                    earned_income_rate * earned_income_amount
                ) / (phase_out_end - phase_out_start)
                eitc.phase_out.rate.brackets[i].amount.update(
                    period=period, value=phase_out_rate
                )

        branch.tax_benefit_system.modify_parameters(modify_parameters)

        amount = (
            branch.calculate("earned_income_tax_credit", period)
            * current_ca_eitc.adjustment.factor
        )

        secondary_schedule_amount = (
            tax_unit("ca_eitc_secondary_schedule", period)
            / current_ca_eitc.adjustment.divisor
        )

        count_children = tax_unit("eitc_child_count", period)

        return where(
            amount
            > current_ca_eitc.secondary_schedule.threshold.calc(
                count_children
            ),
            amount,
            secondary_schedule_amount,
        )


class ca_eitc_secondary_schedule(Variable):
    value_type = float
    entity = TaxUnit
    label = "CalEITC amount"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/file/personal/credits/california-earned-income-tax-credit.html#What-you-ll-get"

    def formula(tax_unit, period, parameters):
        simulation: Simulation = tax_unit.simulation
        branch = simulation.get_branch("ca_eitc")
        branch.tax_benefit_system = branch.tax_benefit_system.clone()
        current_ca_eitc = parameters(
            period
        ).gov.states.ca.tax.income.credits.earned_income

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
                period=period, value=current_ca_eitc.max_age
            )
            eitc.eligibility.age.min.update(
                period=period, value=current_ca_eitc.min_age
            )

            # Investment income change
            eitc.phase_out.max_investment_income.update(
                period=period, value=current_ca_eitc.max_investment_income
            )

            # EITC amount and phase-out amount changes
            for i in range(len(eitc.max.brackets)):
                ca_i = min(
                    i, len(ca_eitc.earned_income_amount.brackets) - 1
                )  # Federal policy having more brackets => use the top of CA's policy
                for attribute in ["amount", "threshold"]:
                    getattr(eitc.max.brackets[i], attribute).update(
                        period=period,
                        value=getattr(
                            ca_eitc.secondary_schedule.earned_income_amount.brackets[
                                ca_i
                            ],
                            attribute,
                        )(period),
                    )
                    getattr(
                        eitc.phase_out.start.brackets[i], attribute
                    ).update(
                        period=period,
                        value=getattr(
                            ca_eitc.secondary_schedule.phase_out_amount.brackets[
                                ca_i
                            ],
                            attribute,
                        )(period),
                    )

                # Phase-out by $30k -> phase-out rate(i) = (earned_income_rate(i) * earned_income_amount(i)) / (30k - phase_out_start(i))

                earned_income_rate = (
                    ca_eitc.secondary_schedule.phase_in.rate.brackets[
                        ca_i
                    ].amount(period)
                )
                earned_income_amount = current_ca_eitc.secondary_schedule.earned_income_amount.amounts[
                    ca_i
                ]
                phase_out_start = current_ca_eitc.secondary_schedule.phase_out_amount.amounts[
                    ca_i
                ]
                phase_out_end = current_ca_eitc.max_earnings
                phase_out_rate = (
                    earned_income_rate * earned_income_amount
                ) / (phase_out_end - phase_out_start)
                eitc.phase_out.rate.brackets[i].amount.update(
                    period=period, value=phase_out_rate
                )

        branch.tax_benefit_system.modify_parameters(modify_parameters)

        return (
            branch.calculate("earned_income_tax_credit", period)
            * current_ca_eitc.adjustment.factor
        )
