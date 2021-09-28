from openfisca_core.taxbenefitsystems import TaxBenefitSystem
from openfisca_us.entities import *
from openfisca_us.situation_examples import single_filer
import os

COUNTRY_DIR = os.path.dirname(os.path.abspath(__file__))


# Our country tax and benefit class inherits from the general TaxBenefitSystem class.
# The name CountryTaxBenefitSystem must not be changed, as all tools of the OpenFisca ecosystem expect a CountryTaxBenefitSystem class to be exposed in the __init__ module of a country package.
class CountryTaxBenefitSystem(TaxBenefitSystem):
    CURRENCY = "$"

    def __init__(self):
        # We initialize our tax and benefit system with the general constructor
        super().__init__(entities)

        # We add to our tax and benefit system all the variables
        self.add_variables_from_directory(
            os.path.join(COUNTRY_DIR, "variables")
        )

        # We add to our tax and benefit system all the legislation parameters defined in the  parameters files
        param_path = os.path.join(COUNTRY_DIR, "parameters")
        self.load_parameters(param_path)

        # We define which variable, parameter and simulation example will be used in the OpenAPI specification
