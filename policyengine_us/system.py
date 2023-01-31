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
from policyengine_us.data import CPS
from policyengine_us.tools.taxcalc.generate_taxcalc_variable import (
    add_taxcalc_variable_aliases,
)
from policyengine_us.variables.household.demographic.geographic.state.in_state import (
    create_50_state_variables,
)
from policyengine_us.tools.parameters import backdate_parameters

COUNTRY_DIR = Path(__file__).parent


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

    def __init__(self):
        # We initialize our tax and benefit system with the general constructor
        super().__init__(entities)

        self.add_variables(*create_50_state_variables())

        self.parameters = set_irs_uprating_parameter(self.parameters)
        self.parameters = backdate_parameters(self.parameters)

        add_taxcalc_variable_aliases(self)


system = CountryTaxBenefitSystem()


class Simulation(CoreSimulation):
    default_tax_benefit_system = CountryTaxBenefitSystem
    default_tax_benefit_system_instance = system
    default_role = "member"
    default_calculation_period = 2022
    default_input_period = 2022


class Microsimulation(CoreMicrosimulation):
    default_tax_benefit_system = CountryTaxBenefitSystem
    default_tax_benefit_system_instance = system
    default_dataset = CPS
    default_dataset_year = 2023
    default_role = "member"
    default_calculation_period = 2023
    default_input_period = 2023


class IndividualSim(CoreIndividualSim):  # Deprecated
    tax_benefit_system = CountryTaxBenefitSystem
    entities = {entity.key: entity for entity in entities}
    default_dataset = CPS

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


if 2023 not in CPS.years:
    CPS.download(2023)

if 2022 not in CPS.years:
    CPS.download(2022)

if 2021 not in CPS.years:
    CPS.download(2021)
