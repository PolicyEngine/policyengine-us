from .winship import create_eitc_winship_reform


def create_structural_reforms_from_parameters(parameters, period):
    return create_eitc_winship_reform(parameters, period)
