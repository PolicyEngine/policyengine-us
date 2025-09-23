from policyengine_us.model_api import *


class tx_dart_enrolled_in_applicable_programs(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Dallas Area Rapid Transit (DART) Discount GoPass program"
    definition_period = YEAR
    defined_for = StateCode.TX
    reference = "https://www.dart.org/fare/general-fares-and-overview/discount-gopass-tap-card"

    # The Discount GoPass program provides 50% fare reduction for riders enrolled
    # in qualifying assistance programs. This uses the 'adds' parameter to check
    # if the person receives benefits from any program listed in qualifying_programs.yaml
    # (SNAP, Medicaid, Medicare, CHIP, TANF, WIC, etc.)
    # Note: Some programs like CEAP and DHA Housing are listed but not yet modeled
    adds = "gov.states.tx.dart.qualifying_programs"
