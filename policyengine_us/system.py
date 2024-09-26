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
import ast
import glob
import os

# Define these in advance to allow for structural variable parsing
from policyengine_core.data_structures.unit import Unit
from policyengine_core.periods import DAY, ETERNITY, MONTH, YEAR, period

from typing import Dict, Any

USD = Unit.USD

COUNTRY_DIR = Path(__file__).parent

CURRENT_YEAR = 2024
year_start = str(CURRENT_YEAR) + "-01-01"


class CountryTaxBenefitSystem(TaxBenefitSystem):
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

        self.structural_reform_variables = {}

        self.load_parameters(COUNTRY_DIR / "parameters")
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
        self.add_abolition_parameters()
        add_default_uprating(self)

        # Store all structural variables in a dictionary. These variables
        # could be created if a structural reform is enacted, otherwise will not
        # exist in the model
        self.structural_variables: Dict[str, Any] = self.parse_structural_variables_from_dir(COUNTRY_DIR / "reforms")

        structural_reform = create_structural_reforms_from_parameters(
            self.parameters, year_start
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

    def parse_structural_variables_from_dir(self, dir_path: str | Path) -> list[Dict[str, Any]]:
        py_files = glob.glob(os.path.join(dir_path, "*.py"))

        parsed_vars = []

        for py_file in py_files:
            new_vars = self.parse_structural_variables_from_file(py_file)
            parsed_vars.extend(new_vars)
        subdirectories = glob.glob(os.path.join(dir_path, "*/"))

        for subdirectory in subdirectories:
            new_vars = self.parse_structural_variables_from_dir(subdirectory)
            parsed_vars.extend(new_vars)
        
        return parsed_vars

    def parse_structural_variables_from_file(self, file_path: str | Path) -> list[Dict[str, Any]]:

        def extract_attributes(class_def):
            """
            Helper function to extract attributes from a class definition

            We want to be able to extract the following variable attributes, with
            the following possible value types

            value_type: str, int, float, bool, str, None
            entity: Population (policyengine_core)
            label: str
            unit: Unit (policyengine_core) | str
            definition_period: Period (policyengine_core)
            defined_for: str | StateCode (policyengine_us)

            This requires various different extraction methods out of the AST, which will
            be noted individually below

            """

            attributes = {}

            # Iterate over every syntax tree node in the class definition
            for node in class_def.body:
                
                # If assigning a value...
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        
                        # and we reach a name node...
                        if isinstance(target, ast.Name):
                            
                            # Begin assigning attributes based on the target
                            
                            # If the variable represents any form of constant value
                            # (label, str unit, str defined_for, value_type)
                            if isinstance(node.value, ast.Constant):
                                attributes[target.id] = node.value.value

                            # Otherwise, if we're still assinging something...
                            elif isinstance(node.value, ast.Name):
                              try:
                                  # Try to evaluate the variable
                                  obj = eval(node.value.id)

                                  # Check if we have a class instance with a key attribute (entity)
                                  if hasattr(obj, 'key'):
                                      attributes[target.id] = obj.key

                                  # Otherwise, just return either the class (value_type) or the string
                                  # (label, defined_for, definition_period, unit)
                                  else:
                                      attributes[target.id] = obj
                              except NameError as e:
                                  # If the name isn't in the current namespace, set None
                                  print(f"NameError while parsing structural variable {target.id}'s {node.value.id} attribute:")
                                  print(e)
                                  attributes[target.id] = None
            return attributes
        
        # Read the content of the file
        with open(file_path, 'r') as file:
            source = file.read()

        # Parse the source code into an AST
        tree = ast.parse(source)

        variables = []

        # Walk through the entire AST and find class definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if the class inherits from Variable
                if any(base.id == 'Variable' for base in node.bases if isinstance(base, ast.Name)):

                    # Do not include the variable if it already exists in the system
                    if node.name in self.variables:
                        continue

                    variable_info = {
                        'name': node.name,
                        **extract_attributes(node)
                    }
                    variables.append(variable_info)

        return variables

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

class Microsimulation(CoreMicrosimulation):
    default_tax_benefit_system = CountryTaxBenefitSystem
    default_tax_benefit_system_instance = system
    default_dataset = CPS_2024
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

        self.input_variables = [
            variable
            for variable in self.input_variables
            if variable
            not in [
                "employment_income",
                "self_employment_income",
                "weekly_hours_worked",
            ]
        ] + [
            "employment_income_before_lsr",
            "self_employment_income_before_lsr",
            "weekly_hours_worked_before_lsr",
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
