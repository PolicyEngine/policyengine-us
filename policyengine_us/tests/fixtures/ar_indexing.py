"""Complete synthetic CPI windows for Arkansas indexing mechanism tests."""

from policyengine_core.model_api import Reform
from policyengine_core.parameters import Parameter
from policyengine_core.parameters.operations.uprate_parameters import uprate_parameters
from policyengine_core.periods import instant

from policyengine_us.parameters.uprating_extensions import set_all_uprating_parameters


def install_monthly_window(parameter, first_month, value):
    """Replace all twelve observations, including any missing baseline month."""
    start = instant(first_month)
    for month in range(12):
        parameter.update(period=f"month:{start.offset(month, 'month')}:1", value=value)


def _synthetic_indexing(parameters, cpi_u_factor, chained_factor):
    cpi = parameters.gov.bls.cpi
    install_monthly_window(cpi.cpi_u, "2024-09-01", 100)
    install_monthly_window(cpi.cpi_u, "2025-09-01", 100 * cpi_u_factor)
    # Preserve the shared IRS index's existing August-July window. This
    # makes its growth intentionally differ from Arkansas's CPI-U growth.
    install_monthly_window(cpi.c_cpi_u, "2024-08-01", 100)
    install_monthly_window(cpi.c_cpi_u, "2025-08-01", 100 * chained_factor)

    main = parameters.gov.states.ar.tax.income.rates.main
    for parameter in main.get_descendants():
        if isinstance(parameter, Parameter) and parameter.metadata.get("uprating"):
            parameter.update(
                start=instant("2026-01-01"),
                value=parameter("2026-01-01"),
                remove_after=True,
            )

    set_all_uprating_parameters(parameters)
    return uprate_parameters(parameters)


def _indexing_reform(cpi_u_factor, chained_factor):
    class reform(Reform):
        def apply(self):
            self.modify_parameters(
                lambda parameters: _synthetic_indexing(
                    parameters, cpi_u_factor, chained_factor
                )
            )

    return reform


ar_cpi_four_percent_chained_one_percent = _indexing_reform(1.04, 1.01)
ar_cpi_one_percent_chained_four_percent = _indexing_reform(1.01, 1.04)
ar_cpi_minus_one_percent_chained_four_percent = _indexing_reform(0.99, 1.04)
