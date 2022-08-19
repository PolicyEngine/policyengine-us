from openfisca_core.taxbenefitsystems import TaxBenefitSystem
from openfisca_us.entities import *
from openfisca_us.parameters.gov.irs.uprating import set_irs_uprating_parameter
from openfisca_us.situation_examples import single_filer
from openfisca_tools import (
    homogenize_parameter_structures,
    uprate_parameters,
    propagate_parameter_metadata,
)
import os
from openfisca_us.tools.backdate_parameters import backdate_parameters

from openfisca_us.tools.dev.taxcalc.generate_taxcalc_variable import (
    add_taxcalc_variable_aliases,
)
from openfisca_us.variables.household.demographic.geographic.state.in_state import (
    create_50_state_variables,
)

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

        self.add_variables(*create_50_state_variables())

        # We add to our tax and benefit system all the legislation parameters defined in the  parameters files
        param_path = os.path.join(COUNTRY_DIR, "parameters")
        self.load_parameters(param_path)

        self.parameters = homogenize_parameter_structures(
            self.parameters, self.variables
        )

        self.parameters = propagate_parameter_metadata(self.parameters)

        self.parameters = set_irs_uprating_parameter(self.parameters)

        self.parameters = uprate_parameters(self.parameters)

        self.parameters = backdate_parameters()(self.parameters)

        # Add taxcalc aliases

        add_taxcalc_variable_aliases(self)
