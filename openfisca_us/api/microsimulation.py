from openfisca_tools import Microsimulation as GeneralMicrosimulation
from openfisca_us import CountryTaxBenefitSystem
from openfisca_us.entities import entities
from openfisca_us_data import CPS


class Microsimulation(GeneralMicrosimulation):
    tax_benefit_system = CountryTaxBenefitSystem
    entities = entities
    default_dataset = CPS
