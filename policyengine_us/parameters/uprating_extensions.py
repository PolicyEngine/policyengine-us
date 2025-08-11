"""Unified script to extend all uprating factors through 2100."""

from policyengine_us.model_api import *
from policyengine_core.periods import instant


def get_irs_cpi(parameters: ParameterNode, year: int) -> float:
    """Calculate IRS CPI based on Chained CPI-U average from Sep to Aug."""
    cpi = parameters.gov.bls.cpi.c_cpi_u
    end = instant(f"{year}-08-01")
    start = end.offset(-MONTHS_IN_YEAR, MONTH)
    monthly_cpi_values = []
    for month in range(MONTHS_IN_YEAR):
        monthly_cpi_values += [cpi(start.offset(month, MONTH))]
    return sum(monthly_cpi_values) / MONTHS_IN_YEAR


def extend_parameter_values(
    parameter: Parameter,
    last_projected_year: int,
    end_year: int,
    period_month: int = 1,
    period_day: int = 1,
) -> None:
    """
    Extend a parameter's values from last_projected_year to end_year using
    the growth rate from the last two years of projections.

    Args:
        parameter: The parameter to extend
        last_projected_year: The last year with actual/projected values
        end_year: The year to extend values through
        period_month: The month for the period (default 1 for January)
        period_day: The day for the period (default 1)
    """
    # Calculate the growth rate from the last two years of projections
    date_format = f"-{period_month:02d}-{period_day:02d}"
    second_to_last_value = parameter(f"{last_projected_year - 1}{date_format}")
    last_value = parameter(f"{last_projected_year}{date_format}")
    growth_rate = last_value / second_to_last_value

    # Apply growth rate for years beyond projections
    for year in range(last_projected_year + 1, end_year + 1):
        previous_value = parameter(f"{year - 1}{date_format}")
        new_value = previous_value * growth_rate
        parameter.update(period=f"year:{year}{date_format}:1", value=new_value)

    # Set the final value for periods after the last year
    final_value = parameter(f"{end_year}{date_format}")
    parameter.update(
        start=instant(f"{end_year}{date_format}"), value=final_value
    )


def set_all_uprating_parameters(parameters: ParameterNode) -> ParameterNode:
    """
    Extend all uprating parameters through 2100.

    This function programmatically extends various uprating factors used
    throughout the US tax and benefit system, including:
    - IRS uprating (based on Chained CPI-U)
    - SNAP uprating (October values)
    - SSA uprating (January values)
    - HHS poverty guideline uprating (January values)
    """
    END_YEAR = 2100

    # IRS uprating - special case that computes from CPI
    IRS_UPRATING_START_YEAR = 2010
    IRS_LAST_PROJECTED_YEAR = 2035

    uprating_index = parameters.gov.irs.uprating

    # Calculate the growth rate from the last two years of CPI projections
    cpi_second_to_last = get_irs_cpi(parameters, IRS_LAST_PROJECTED_YEAR - 2)
    cpi_last = get_irs_cpi(parameters, IRS_LAST_PROJECTED_YEAR - 1)
    growth_rate = cpi_last / cpi_second_to_last

    # Apply IRS uprating
    for year in range(IRS_UPRATING_START_YEAR, END_YEAR + 1):
        if year <= IRS_LAST_PROJECTED_YEAR:
            # Use actual CPI values through the last projected year
            irs_cpi = get_irs_cpi(parameters, year - 1)
        else:
            # For all years after LAST_PROJECTED_YEAR, apply the constant growth rate
            irs_cpi = uprating_index(f"{year - 1}-01-01") * growth_rate
        uprating_index.update(period=f"year:{year}-01-01:1", value=irs_cpi)
    uprating_index.update(start=instant(f"{END_YEAR}-01-01"), value=irs_cpi)

    # SNAP uprating (October values, last projection year 2034)
    extend_parameter_values(
        parameters.gov.usda.snap.uprating,
        last_projected_year=2034,
        end_year=END_YEAR,
        period_month=10,
        period_day=1,
    )

    # SSA uprating (January values, last projection year 2035)
    extend_parameter_values(
        parameters.gov.ssa.uprating,
        last_projected_year=2035,
        end_year=END_YEAR,
        period_month=1,
        period_day=1,
    )

    # HHS poverty guideline uprating (January values, last projection year 2035)
    extend_parameter_values(
        parameters.gov.hhs.uprating,
        last_projected_year=2035,
        end_year=END_YEAR,
        period_month=1,
        period_day=1,
    )

    # CPI-U (February values, last projection year 2034)
    extend_parameter_values(
        parameters.gov.bls.cpi.cpi_u,
        last_projected_year=2034,
        end_year=END_YEAR,
        period_month=2,
        period_day=1,
    )

    # Chained CPI-U (February values, last projection year 2034)
    extend_parameter_values(
        parameters.gov.bls.cpi.c_cpi_u,
        last_projected_year=2034,
        end_year=END_YEAR,
        period_month=2,
        period_day=1,
    )

    # CPI-W (February values, last projection year 2034)
    extend_parameter_values(
        parameters.gov.bls.cpi.cpi_w,
        last_projected_year=2034,
        end_year=END_YEAR,
        period_month=2,
        period_day=1,
    )

    return parameters
