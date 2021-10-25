from openfisca_tools import IndividualSim as GeneralIndividualSim
from openfisca_us import CountryTaxBenefitSystem
from openfisca_us.entities import entities
from openfisca_us_data import CPS


class IndividualSim(GeneralIndividualSim):
    tax_benefit_system = CountryTaxBenefitSystem
    entities = {entity.key: entity for entity in entities}
    default_dataset = CPS
