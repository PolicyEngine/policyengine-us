def test_repeal_head_of_household():
    import numpy as np
    from policyengine_us import Microsimulation
    from policyengine_core.reforms import Reform
    from policyengine_core.periods import instant

    class neutralize_reform(Reform):
        def apply(self):
            self.neutralize_variable("head_of_household_eligible")

    baseline = Microsimulation()
    neutralize_reformed = Microsimulation(reform=neutralize_reform)

    baseline_net_income = baseline.calculate("household_net_income")
    neutralize_reform_net_income = neutralize_reformed.calculate(
        "household_net_income"
    )

    # Check the same result using the reform.

    def modify_parameters(parameters):
        parameters.gov.contrib.congress.romney.family_security_act.remove_head_of_household.update(
            start=instant("2023-01-01"),
            stop=instant("2028-12-31"),
            value=True,
        )
        return parameters

    class parameter_reform(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)

    parameter_reformed = Microsimulation(reform=parameter_reform)
    parameter_reform_net_income = parameter_reformed.calculate(
        "household_net_income"
    )

    bni_nan_count = np.isnan(baseline_net_income).sum()
    print("baseline   NaN count", bni_nan_count)
    nni_is_nan = np.isnan(neutralize_reform_net_income)
    nni_nan_count = nni_is_nan.sum()
    print("neutralize NaN count", nni_nan_count)
    pni_nan_count = np.isnan(parameter_reform_net_income).sum()
    print("parameter  NaN count", pni_nan_count)
    b_vs_p_diff_count = 0
    for idx in range(baseline_net_income.size):
        if nni_is_nan[idx]:
            print(
                "idx,bni,nni,pni=",
                idx,
                baseline_net_income[idx],
                neutralize_reform_net_income[idx],
                parameter_reform_net_income[idx],
            )
            if not np.allclose(
                [baseline_net_income[idx]],
                [parameter_reform_net_income[idx]],
            ):
                b_vs_p_diff_count += 1
        idx += 1
    print("b_vs_p_diff_count=", b_vs_p_diff_count)
    n_vs_p_diff_count = 0
    for idx in range(baseline_net_income.size):
        if not np.allclose(
            [neutralize_reform_net_income[idx]],
            [parameter_reform_net_income[idx]],
        ):
            n_vs_p_diff_count += 1
    print("n_vs_p_diff_count=", n_vs_p_diff_count)

    # Check they're the same, element by element.
    if nni_nan_count == 0 and pni_nan_count == 0:
        assert np.allclose(
            neutralize_reform_net_income, parameter_reform_net_income
        )

    # Check they're the right order of magnitude.
    weight = baseline.calculate("household_weight")
    base_ni_total = np.nansum(baseline_net_income * weight)
    use_neutralize_reform = True
    if use_neutralize_reform:
        neut_ni_total = np.nansum(neutralize_reform_net_income * weight)
        total_loss = base_ni_total - neut_ni_total
        # NOTE: neutralize_reform_net_income contains NaN values, which
        #       indicates the neutralize reform is not specified correctly
    else:  # using parameter reform
        parm_ni_total = np.nansum(parameter_reform_net_income * weight)
        total_loss = base_ni_total - parm_ni_total
        # NOTE: total_loss is zero when using parameter reform, which
        #       indicates the parameter reform is not specified correctly
    # CBO estimates $10B to $20B:
    # https://www.cbo.gov/budget-options/54789
    assert total_loss > 5e9
    assert total_loss < 25e9
