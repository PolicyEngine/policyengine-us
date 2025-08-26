from policyengine_us.model_api import *
from numpy.typing import ArrayLike


class id_liheap_income_limit(Variable):
    value_type = float
    entity = Person
    label = "Idaho LIHEAP income limit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.eicap.org/our-programs/family-services/energy-assistance-winter-heating-program/"

    def formula(person, period, parameters):
        # Get household size from SPM unit
        spm_unit = person.spm_unit
        household_size = spm_unit.nb_persons()
        
        # Get the parameter tree
        p = parameters(period).gov.states.id.dhw.liheap.income_limit
        
        # Determine which bracket to use based on household size
        # The parameter structure uses household size as the key
        # We need to cap at 8 for 8+ person households
        size_for_limit = min_(household_size, 8)
        
        # Get monthly limit from parameters
        monthly_limit = p.calc(size_for_limit)
        
        # Convert to annual amount
        return monthly_limit * 12