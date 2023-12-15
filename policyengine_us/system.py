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
from policyengine_us.data import DATASETS, CPS_2023
from policyengine_us.variables.household.demographic.geographic.state.in_state import (
    create_50_state_variables,
)
from policyengine_us.tools.parameters import backdate_parameters
from policyengine_us.reforms import create_structural_reforms_from_parameters

COUNTRY_DIR = Path(__file__).parent

CURRENT_YEAR = 2023
year_start = str(CURRENT_YEAR) + "-01-01"


class CountryTaxBenefitSystem(TaxBenefitSystem):
    parameters_dir = COUNTRY_DIR / "parameters"
    variables_dir = COUNTRY_DIR / "variables"
    auto_carry_over_input_variables = True
    basic_inputs = [
        "state_name",
        "employment_income",
        "age",
    ]
    modelled_policies = COUNTRY_DIR / "modelled_policies.yaml"

    def __init__(self, reform=None):
        super().__init__(entities, reform=reform)

        reform = create_structural_reforms_from_parameters(
            self.parameters, year_start
        )
        if reform is not None:
            reform.apply(self)

        self.add_variables(*create_50_state_variables())

        self.parameters = set_irs_uprating_parameter(self.parameters)
        self.parameters = backdate_parameters(
            self.parameters, first_instant="2020-01-01"
        )


system = CountryTaxBenefitSystem()


class Simulation(CoreSimulation):
    default_tax_benefit_system = CountryTaxBenefitSystem
    default_tax_benefit_system_instance = system
    default_role = "member"
    default_calculation_period = CURRENT_YEAR
    default_input_period = CURRENT_YEAR
    datasets = DATASETS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        reform = create_structural_reforms_from_parameters(
            self.tax_benefit_system.parameters, year_start
        )
        if reform is not None:
            self.apply_reform(reform)


class Microsimulation(CoreMicrosimulation):
    default_tax_benefit_system = CountryTaxBenefitSystem
    default_tax_benefit_system_instance = system
    default_dataset = CPS_2023
    default_dataset_year = CURRENT_YEAR
    default_role = "member"
    default_calculation_period = CURRENT_YEAR
    default_input_period = CURRENT_YEAR
    datasets = DATASETS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        reform = create_structural_reforms_from_parameters(
            self.tax_benefit_system.parameters, year_start
        )
        if reform is not None:
            self.apply_reform(reform)


class IndividualSim(CoreIndividualSim):  # Deprecated
    tax_benefit_system = CountryTaxBenefitSystem
    entities = {entity.key: entity for entity in entities}
    default_dataset = CPS_2023

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
