from pathlib import Path
from policyengine_core.taxbenefitsystems import TaxBenefitSystem
from policyengine_us.entities import *
from policyengine_us.parameters.gov.irs.uprating import (
    set_irs_uprating_parameter,
)
from policyengine_core.simulations import (
    Simulation as CoreSimulation,
    Microsimulation as CoreMicrosimulation,
    IndividualSim as CoreIndividualSim,
)
from policyengine_us.variables.household.demographic.geographic.state.in_state import (
    create_50_state_variables,
)
from policyengine_us.tools.parameters import backdate_parameters
from policyengine_us.reforms import create_structural_reforms_from_parameters
from policyengine_core.parameters.operations.homogenize_parameters import (
    homogenize_parameter_structures,
)
from policyengine_core.parameters.operations.interpolate_parameters import (
    interpolate_parameters,
)
from policyengine_core.parameters.operations.propagate_parameter_metadata import (
    propagate_parameter_metadata,
)
from policyengine_core.parameters.operations.uprate_parameters import (
    uprate_parameters,
)
from .tools.default_uprating import add_default_uprating
from policyengine_us_data import DATASETS, CPS_2024

from typing import Annotated


COUNTRY_DIR = Path(__file__).parent

CURRENT_YEAR = 2024
DEFAULT_START_DATE = str(CURRENT_YEAR) + "-01-01"


class CountryTaxBenefitSystem(TaxBenefitSystem):
    """
    The tax-benefit system for the United States.
    This structure is a modification of the -core
    package's base TaxBenefitSystem class.

    Args:
        reform (tuple | None): A tuple of reforms to apply to the system.
        If no reform is applied, the system will be initialized with the
        default tax/benefit parameters.

        start_instant(str: ISO date format YYYY-MM-DD): Optional; The date
        at which the simulation begins; defaults to 2024-01-01; this is a
        temporary patch for structural reforms, and must be set to the start
        date of a structural reform parameter if it begins on a date other
        than the first day of the current year.
    """

    variables_dir = COUNTRY_DIR / "variables"
    auto_carry_over_input_variables = True
    basic_inputs = [
        "state_name",
        "employment_income",
        "age",
    ]
    modelled_policies = COUNTRY_DIR / "modelled_policies.yaml"

    def __init__(
        self,
        reform: tuple | None = None,
        start_instant: Annotated[
            str, "ISO date format YYYY-MM-DD"
        ] = DEFAULT_START_DATE,
    ):
        super().__init__(entities, reform=reform)
        self.load_parameters(COUNTRY_DIR / "parameters")
        self.add_abolition_parameters()
        if reform:
            self.apply_reform_set(reform)
        self.parameters = set_irs_uprating_parameter(self.parameters)
        self.parameters = homogenize_parameter_structures(
            self.parameters, self.variables
        )
        self.parameters = propagate_parameter_metadata(self.parameters)
        self.parameters = interpolate_parameters(self.parameters)
        self.parameters = uprate_parameters(self.parameters)
        self.parameters = propagate_parameter_metadata(self.parameters)
        add_default_uprating(self)

        structural_reform = create_structural_reforms_from_parameters(
            self.parameters, start_instant
        )
        if reform is None:
            reform = ()
        reform = (reform, structural_reform)

        self.parameters = backdate_parameters(
            self.parameters, first_instant="2015-01-01"
        )

        for parameter in self.parameters.get_descendants():
            parameter.modified = False

        if reform is not None:
            self.apply_reform_set(reform)

        self.add_variables(*create_50_state_variables())


system = CountryTaxBenefitSystem()


class Simulation(CoreSimulation):
    """
    A simulation of the tax-benefit system for the United States,
    defined against the base simulation class in the -core package.

    This simulation is commonly used for household-level impacts, as it
    does not include society-wide microdata.

    Args:
        start_instant(str: ISO date format YYYY-MM-DD): Optional; The date
        at which the simulation begins; defaults to 2024-01-01; this is a
        temporary patch for structural reforms, and must be set to the start
        date of a structural reform parameter if it begins on a date other
        than the first day of the current year.
    """

    default_tax_benefit_system = CountryTaxBenefitSystem
    default_tax_benefit_system_instance = system
    default_role = "member"
    default_calculation_period = CURRENT_YEAR
    default_input_period = CURRENT_YEAR
    datasets = DATASETS

    def __init__(self, *args, **kwargs):
        start_instant: Annotated[str, "ISO date format YYYY-MM-DD"] = (
            kwargs.pop("start_instant", DEFAULT_START_DATE)
        )
        super().__init__(*args, **kwargs)

        reform = create_structural_reforms_from_parameters(
            self.tax_benefit_system.parameters, start_instant
        )
        if reform is not None:
            self.apply_reform(reform)

        # Labor supply responses

        employment_income = self.get_holder("employment_income")
        for known_period in employment_income.get_known_periods():
            array = employment_income.get_array(known_period)
            self.set_input("employment_income_before_lsr", known_period, array)
            employment_income.delete_arrays(known_period)

        self_employment_income = self.get_holder("self_employment_income")
        for known_period in employment_income.get_known_periods():
            array = self_employment_income.get_array(known_period)
            self.set_input(
                "self_employment_income_before_lsr", known_period, array
            )
            self_employment_income.delete_arrays(known_period)

        weekly_hours = self.get_holder("weekly_hours_worked")
        for known_period in weekly_hours.get_known_periods():
            array = weekly_hours.get_array(known_period)
            self.set_input(
                "weekly_hours_worked_before_lsr", known_period, array
            )
            weekly_hours.delete_arrays(known_period)

        # Capital gains responses

        cg_holder = self.get_holder("long_term_capital_gains")
        for known_period in cg_holder.get_known_periods():
            array = cg_holder.get_array(known_period)
            self.set_input(
                "long_term_capital_gains_before_response", known_period, array
            )
            cg_holder.delete_arrays(known_period)


class Microsimulation(CoreMicrosimulation):
    """
    A microsimulation of the tax-benefit system for the United States,
    defined against the base microsimulation class in the -core package.

    This simulation contains society-wide representative microdata, and is
    thus suitable for society-level impacts.

    Args:
        start_instant(str: ISO date format YYYY-MM-DD): Optional; The date
        at which the simulation begins; defaults to 2024-01-01; this is a
        temporary patch for structural reforms, and must be set to the start
        date of a structural reform parameter if it begins on a date other
        than the first day of the current year.
    """

    default_tax_benefit_system = CountryTaxBenefitSystem
    default_tax_benefit_system_instance = system
    default_dataset = CPS_2024
    default_dataset_year = CURRENT_YEAR
    default_role = "member"
    default_calculation_period = CURRENT_YEAR
    default_input_period = CURRENT_YEAR
    datasets = DATASETS

    def __init__(self, *args, **kwargs):
        start_instant: Annotated[str, "ISO date format YYYY-MM-DD"] = (
            kwargs.pop("start_instant", DEFAULT_START_DATE)
        )
        super().__init__(*args, **kwargs)

        reform = create_structural_reforms_from_parameters(
            self.tax_benefit_system.parameters, start_instant
        )
        if reform is not None:
            self.apply_reform(reform)

        # Labor supply responses

        employment_income = self.get_holder("employment_income")
        for known_period in employment_income.get_known_periods():
            array = employment_income.get_array(known_period)
            self.set_input("employment_income_before_lsr", known_period, array)
            employment_income.delete_arrays(known_period)

        self_employment_income = self.get_holder("self_employment_income")
        for known_period in self_employment_income.get_known_periods():
            array = self_employment_income.get_array(known_period)
            self.set_input(
                "self_employment_income_before_lsr", known_period, array
            )
            self_employment_income.delete_arrays(known_period)

        weekly_hours = self.get_holder("weekly_hours_worked")
        for known_period in weekly_hours.get_known_periods():
            array = weekly_hours.get_array(known_period)
            self.set_input(
                "weekly_hours_worked_before_lsr", known_period, array
            )
            weekly_hours.delete_arrays(known_period)

        # Capital gains responses

        cg_holder = self.get_holder("long_term_capital_gains")
        for known_period in cg_holder.get_known_periods():
            array = cg_holder.get_array(known_period)
            self.set_input(
                "long_term_capital_gains_before_response", known_period, array
            )
            cg_holder.delete_arrays(known_period)

        self.input_variables = [
            variable
            for variable in self.input_variables
            if variable
            not in [
                "employment_income",
                "self_employment_income",
                "weekly_hours_worked",
                "capital_gains",
            ]
        ] + [
            "employment_income_before_lsr",
            "self_employment_income_before_lsr",
            "weekly_hours_worked_before_lsr",
            "long_term_capital_gains_before_response",
        ]


class IndividualSim(CoreIndividualSim):  # Deprecated
    tax_benefit_system = CountryTaxBenefitSystem
    entities = {entity.key: entity for entity in entities}
    default_dataset = CPS_2024
    default_roles = dict(
        tax_unit="member",
        spm_unit="member",
        household="member",
        family="member",
    )
    required_entities = [
        "tax_unit",
        "spm_unit",
        "household",
        "family",
    ]
