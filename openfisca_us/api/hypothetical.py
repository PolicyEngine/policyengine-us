from policyengine_core import IndividualSim as GeneralIndividualSim
from openfisca_us import CountryTaxBenefitSystem
from openfisca_us.entities import entities
from openfisca_us_data import CPS


class IndividualSim(GeneralIndividualSim):
    tax_benefit_system = CountryTaxBenefitSystem
    entities = entities
    default_dataset = CPS
