from policyengine_us.model_api import *


class tx_dart_reduced_fare_program_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Dallas Area Rapid Transit (DART) Reduced Fare program due to qualifying program enrollment"
    definition_period = YEAR
    defined_for = StateCode.TX
    reference = "https://www.dart.org/fare/general-fares-and-overview/discount-gopass-tap-card"

    # The Discount GoPass program provides 50% fare reduction for riders enrolled
    # in qualifying assistance programs. It is the same as Reduced Fare program.
    # This uses the 'adds' parameter to check if the person receives benefits from any
    # program listed in qualifying_programs.yaml
    # (SNAP, Medicaid, Medicare, CHIP, TANF, WIC, etc.)
    # Note: Some programs like CEAP and DHA Housing are listed but not yet modeled
    adds = "gov.states.tx.dart.qualifying_programs"
