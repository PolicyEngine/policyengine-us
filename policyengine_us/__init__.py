"""
This file defines our country's tax and benefit system.

A tax and benefit system is the higher-level instance in OpenFisca.
Its goal is to model the legislation of a country.
Basically a tax and benefit system contains simulation variables (source code) and legislation parameters (data).

See https://openfisca.org/doc/key-concepts/tax_and_benefit_system.html
"""
from policyengine_us.system import CountryTaxBenefitSystem
from policyengine_us.data import ACS, CPS
from policyengine_core.simulations import (
    Simulation as CoreSimulation,
    Microsimulation as CoreMicrosimulation,
)

DATASETS = [ACS, CPS]


class Simulation(CoreSimulation):
    default_tax_benefit_system = CountryTaxBenefitSystem
    default_role = "member"


class Microsimulation(CoreMicrosimulation):
    default_tax_benefit_system = CountryTaxBenefitSystem
    default_dataset = CPS
    default_dataset_year = 2021
    default_role = "member"
