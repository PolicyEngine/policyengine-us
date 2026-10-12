from policyengine_us.model_api import *


class ca_cc_general_assistance_maximum_grant(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Contra Costa County General Assistance maximum grant"
    definition_period = MONTH
    defined_for = "ca_cc_general_assistance_eligible_person"
    reference = "https://ehsd.org/aging-and-adult-services/general-assistance/"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.cc.general_assistance.amount
        eligible_persons = spm_unit.members(
            "ca_cc_general_assistance_eligible_person", period
        )
        num_eligible = spm_unit.sum(eligible_persons)
        # GA aids a single adult ($336) or an eligible couple ($454). Exactly two
        # eligible adults get the couple grant; we do not verify they are married
        # to each other (marital pairing is not tracked within the SPM unit).
        # NOTE: 3+ eligible adults in one SPM unit should not happen in practice
        # -- each adult or couple is a separate GA case -- so any count other than
        # two falls through to the single standard as a safe default.
        return where(num_eligible == 2, p.married, p.single)
