"""Preserve exact multi-year benefit sources in PE-US wrapper simulations."""

import numpy as np
from policyengine_core.periods import YEAR
from policyengine_core.periods import period as to_period
from policyengine_core.simulations import Simulation as CoreSimulation

from policyengine_us.tools.social_security_benefit_levers import (
    SocialSecurityBenefitSource,
    SocialSecurityFund,
)
from policyengine_us.tools.social_security_inputs import SOCIAL_SECURITY_COMPONENTS


class SocialSecurityPeriodMixin:
    def _calculate(self, variable_name, period=None):
        if (
            variable_name not in SOCIAL_SECURITY_COMPONENTS
            or period is None
            or period.unit != YEAR
            or period.size == 1
        ):
            return super()._calculate(variable_name, period)
        variable = self.tax_benefit_system.get_variable(variable_name)
        # Core checks neutralization before exact public inputs and caches.
        if variable.is_neutralized:
            return super()._calculate(variable_name, period)
        try:
            abolished = self.tax_benefit_system.parameters(period).gov.abolitions[
                variable_name
            ]
        except Exception:
            abolished = False
        if abolished:
            return super()._calculate(variable_name, period)
        holder = self.get_holder(variable_name)
        if holder.get_array(period, self.branch_name) is not None:
            return super()._calculate(variable_name, period)
        reported_name = f"{variable_name}_reported"
        base_name = f"{variable_name}_base"
        base_periods = self._get_set_input_periods(base_name)
        has_exact_base = period in base_periods
        if not has_exact_base and period not in self._get_set_input_periods(
            reported_name
        ):
            return super()._calculate(variable_name, period)

        input_state = self._calculation_start()
        base_variable = self.tax_benefit_system.get_variable(base_name)
        try:
            base_abolished = self.tax_benefit_system.parameters(period).gov.abolitions[
                base_name
            ]
        except Exception:
            base_abolished = False
        if has_exact_base or base_variable.is_neutralized or base_abolished:
            # Let Core preserve exact base-input and neutralization precedence.
            amount = CoreSimulation.calculate(self, base_name, period)
        else:
            if any(
                known.start <= period.stop and known.stop >= period.start
                for known in base_periods
            ):
                raise ValueError(
                    "A multi-year reported input with base overrides for other "
                    "periods requires separately supplied annual source amounts"
                )
            amount = CoreSimulation.calculate(self, reported_name, period)
        nonzero = amount != 0
        # Core accepts a stored multi-year YEAR input before checking period
        # consistency. A uniform multiplier needs no annual allocation, while
        # differing annual multipliers need separately supplied annual sources.
        common_factor = None
        for year_number in range(period.start.year, period.stop.year + 1):
            year = to_period(year_number)
            source = CoreSimulation.calculate(self, f"{variable_name}_source", year)
            if np.any(source != SocialSecurityBenefitSource.reported):
                raise NotImplementedError(
                    "Multi-year Social Security sources require the reported route; "
                    "calculated source modes are reserved"
                )
            factor = np.ones_like(amount)
            for name in (
                f"{variable_name}_joint_cola_factor",
                f"{variable_name}_pia_ratio_factor",
                "social_security_across_the_board_factor",
                f"{variable_name}_payable_factor",
            ):
                factor = factor * CoreSimulation.calculate(self, name, year)
            try:
                annual_base_abolished = self.tax_benefit_system.parameters(
                    year
                ).gov.abolitions[base_name]
            except Exception:
                annual_base_abolished = False
            if annual_base_abolished:
                factor = np.zeros_like(factor)
            if (
                variable_name == "social_security_dependents"
                and self.tax_benefit_system.parameters(
                    year
                ).gov.contrib.ssa.benefit_levers.payable.oasi_only
                and np.any(
                    CoreSimulation.calculate(
                        self, "social_security_payable_factor", year
                    )
                    != 1
                )
            ):
                fund = CoreSimulation.calculate(
                    self, "social_security_dependents_fund", year
                )
                if np.any((amount > 0) & (fund == SocialSecurityFund.unspecified)):
                    raise ValueError(
                        "OASI-only payable cuts require the dependent benefit fund"
                    )
            if common_factor is None:
                common_factor = factor
            elif not np.array_equal(common_factor[nonzero], factor[nonzero]):
                raise ValueError(
                    "Social Security levers with differing annual factors on a "
                    "multi-year reported input require separately supplied "
                    "annual source amounts"
                )
        result = self._cast_formula_result(amount * common_factor, variable)
        return self._cache_result(holder, result, period, input_state)
