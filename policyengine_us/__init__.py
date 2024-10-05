"""
This file defines our country's tax and benefit system.

A tax and benefit system is the higher-level instance in PolicyEngine.
Its goal is to model the legislation of a country.
Basically a tax and benefit system contains simulation variables (source code) and legislation parameters (data).

See https://openfisca.org/doc/key-concepts/tax_and_benefit_system.html
"""

from policyengine_us.system import (
    CountryTaxBenefitSystem,
    Simulation,
    Microsimulation,
    IndividualSim,
)
