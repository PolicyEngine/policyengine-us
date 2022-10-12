from openfisca_tools import Microsimulation as GeneralMicrosimulation
from policyengine_us import CountryTaxBenefitSystem
from policyengine_us.entities import entities
from policyengine_us.data import CPS


class Microsimulation(GeneralMicrosimulation):
    tax_benefit_system = CountryTaxBenefitSystem
    entities = entities
    default_dataset = CPS

    def __init__(
        self, reform=(), dataset: type = CPS, year: int = None, **kwargs
    ):
        if dataset == CPS and len(CPS.years) == 0:
            CPS.generate(2021)

        super().__init__(reform, dataset, year)

        self.year = 2022
