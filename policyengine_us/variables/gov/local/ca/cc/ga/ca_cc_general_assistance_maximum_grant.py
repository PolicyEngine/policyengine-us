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
        # When two adults in the unit are eligible we apply the couple grant. We
        # do not verify that the two eligible adults are married to each other;
        # we don't track marital pairing within the SPM unit at the moment.
        return where(num_eligible == 2, p.married, p.single)
