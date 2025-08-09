from policyengine_us.model_api import *
from policyengine_core.periods import instant


def get_irs_cpi(parameters: ParameterNode, year: int) -> float:
    cpi = parameters.gov.bls.cpi.c_cpi_u
    end = instant(f"{year}-08-01")
    start = end.offset(-MONTHS_IN_YEAR, MONTH)
    monthly_cpi_values = []
    for month in range(MONTHS_IN_YEAR):
        monthly_cpi_values += [cpi(start.offset(month, MONTH))]
    return sum(monthly_cpi_values) / MONTHS_IN_YEAR


def set_irs_uprating_parameter(parameters: ParameterNode) -> ParameterNode:

    IRS_UPRATING_START_YEAR = 2010
    IRS_UPRATING_END_YEAR = 2100

    uprating_index: Parameter = parameters.gov.irs.uprating
    # Note: range is inclusive of start and exclusive of end, so we add 1
    for year in range(IRS_UPRATING_START_YEAR, IRS_UPRATING_END_YEAR + 1):
        if year <= 2035:
            # Use actual CPI-U values through 2035
            irs_cpi = get_irs_cpi(parameters, year - 1)
        else:
            # For years after 2035, apply a constant growth rate based on 2034-2035 growth
            if year == 2036:
                # Calculate growth rate from 2034 to 2035
                cpi_2034 = get_irs_cpi(parameters, 2033)
                cpi_2035 = get_irs_cpi(parameters, 2034)
                growth_rate = cpi_2035 / cpi_2034
            # Apply the growth rate for all subsequent years
            irs_cpi = uprating_index(f"{year - 1}-01-01") * growth_rate
        uprating_index.update(period=f"year:{year}-01-01:1", value=irs_cpi)
    uprating_index.update(start=instant(f"{year}-01-01"), value=irs_cpi)
    return parameters
