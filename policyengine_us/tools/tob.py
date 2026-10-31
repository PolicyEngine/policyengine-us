"""Short-lived income-tax counterfactuals for Social Security revenue."""

import gc

from policyengine_us.tools.period_branch import drop_inherited_values


class TobCalculationMixin:
    """Prepare counterfactual states before entering a requested TOB formula.

    Core retains popped branches in active calculation frames. Separate
    outer calculations let those frames finish before the next state is built,
    without modifying Core's dependency tracking. Nested TOB dependencies still
    use the same cached states; their outer caller may retain branch identities
    until it returns.
    """

    def _uses_standard_tob_formula(self, name, period):
        from policyengine_us.system import system

        formula = self.tax_benefit_system.variables[name].get_formula(period)
        standard = system.variables[name].get_formula(period)
        if formula is standard:
            return True
        # A fresh country system reloads unchanged variable source in separate
        # modules. These three formulas use only arguments and literals, so
        # equal code also identifies them without accepting reform functions
        # whose behavior depends on different module globals or closures.
        code = getattr(formula, "__code__", None)
        return (
            code is not None
            and not code.co_names
            and not code.co_freevars
            and code == getattr(standard, "__code__", None)
            and formula.__defaults__ == standard.__defaults__
            and formula.__kwdefaults__ == standard.__kwdefaults__
        )

    def calculate(self, variable_name, period=None, *args, **kwargs):
        if variable_name in (
            "tob_revenue_oasdi",
            "tob_revenue_medicare_hi",
            "tob_revenue_total",
        ):
            calculation_period = (
                period if period is not None else self.default_calculation_period
            )
            holder = self.get_holder(variable_name)
            if (
                not holder.variable.is_neutralized
                and self.get_array(variable_name, calculation_period) is None
                and self._uses_standard_tob_formula(variable_name, calculation_period)
            ):
                needs_total = (
                    variable_name != "tob_revenue_oasdi"
                    and self.get_array("tob_revenue_total", calculation_period) is None
                    and self._uses_standard_tob_formula(
                        "tob_revenue_total", calculation_period
                    )
                )
                needs_oasdi = (
                    variable_name != "tob_revenue_total"
                    and self.get_array("tob_revenue_oasdi", calculation_period) is None
                    and self._uses_standard_tob_formula(
                        "tob_revenue_oasdi", calculation_period
                    )
                )
                states = []
                if needs_total or needs_oasdi:
                    states.append("income_tax_without_social_security")
                if needs_oasdi:
                    states.append("income_tax_with_pre_1993_social_security")
                for state in states:
                    if self.get_array(state, calculation_period) is None:
                        super().calculate(state, calculation_period)
                        gc.collect()
        return super().calculate(variable_name, period, *args, **kwargs)


def income_tax_with_social_security_override(
    simulation, period, *, taxable_social_security=None
):
    """Return only counterfactual income tax, then release its simulation.

    ``None`` neutralizes taxable Social Security; an array supplies an
    alternative inclusion. The caller caches the returned array in an ordinary
    variable holder, so different TOB variables share the counterfactual without
    retaining its other calculated arrays or its cloned tax-benefit system.
    """
    name = (
        "_tob_no_social_security"
        if taxable_social_security is None
        else "_tob_pre_1993_social_security"
    )
    branch = simulation.get_branch(name, clone_system=True)
    try:
        if taxable_social_security is None:
            branch.tax_benefit_system.neutralize_variable(
                "tax_unit_taxable_social_security"
            )
        drop_inherited_values(branch)
        if taxable_social_security is not None:
            branch.get_holder("tax_unit_taxable_social_security").set_input(
                period, taxable_social_security
            )
        # The result must not keep a view into a branch's cached storage.
        return branch.tax_unit("income_tax", period).copy()
    finally:
        simulation.branches.pop(name, None)
        del branch
        # Simulations and populations refer to each other. Collect their cycles
        # before another counterfactual clones the parent simulation.
        gc.collect()
