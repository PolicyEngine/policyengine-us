from openfisca_tools import Microsimulation as GeneralMicrosimulation
from openfisca_us import CountryTaxBenefitSystem
from openfisca_us.entities import entities
from openfisca_us.data import CPS
from openfisca_tools.data import Dataset


class Microsimulation(GeneralMicrosimulation):
    tax_benefit_system = CountryTaxBenefitSystem
    entities = entities
    default_dataset = CPS

    def __init__(
        self, reform=(), dataset: type = CPS, year: int = None, **kwargs
    ):
        if dataset == CPS and len(CPS.years) == 0:
            CPS.generate(2020)

        super().__init__(reform, dataset, year)

        self.year = 2022
