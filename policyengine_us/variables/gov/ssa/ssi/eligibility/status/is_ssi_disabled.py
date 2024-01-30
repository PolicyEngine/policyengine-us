from policyengine_us.model_api import *


class is_ssi_disabled(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Indicates whether a person is disabled for the Supplemental Security Income program"
    label = "SSI disabled"
    reference = "https://www.law.cornell.edu/uscode/text/42/1382c#a_3_A"

    def formula(person, period, parameters):
        # Classify person as disabled for SSI if:
        # 1) They reported receiving SSI due to presumed disability status (being neither aged nor blind); or
        # 2) They are disabled.
        # Earnings in excess of the Substantial Gainful Activity threshold disqualify from either case.
        # First check case 1: SSI reported and neither aged nor blind.
        aged = person("is_ssi_aged", period)
        blind = person("is_blind", period)
        reported_receipt = person("ssi_reported", period) > 0
        reported_disabled_ssi = reported_receipt & ~aged & ~blind
        is_disabled = person("is_disabled", period)
        engaged_in_ssa = person("ssi_engaged_in_sga", period)
        return (reported_disabled_ssi | is_disabled) & ~engaged_in_ssa
