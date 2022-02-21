from openfisca_us.model_api import *
from openfisca_core.periods import instant


def get_irs_cpi(parameters: ParameterNode, year: int) -> float:
    cpi = parameters.bls.cpi.c_cpi_u
    end = instant(f"{year}-08-01")
    start = end.offset(-MONTHS_IN_YEAR, MONTH)
    monthly_cpi_values = []
    for month in range(MONTHS_IN_YEAR):
        monthly_cpi_values += [cpi(start.offset(month, MONTH))]
    return sum(monthly_cpi_values) / MONTHS_IN_YEAR


def set_irs_uprating_parameter(parameters: ParameterNode) -> ParameterNode:
    uprating_index: Parameter = parameters.irs.uprating
    for year in range(2010, 2030):
        irs_cpi = get_irs_cpi(parameters, year - 1)
        uprating_index.update(period=f"year:{year}-01-01:1", value=irs_cpi)
    return parameters
