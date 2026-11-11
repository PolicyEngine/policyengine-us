from policyengine_us.model_api import *


class child_care_subsidies_above_provider_bills(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Child care subsidies above each provider's bill"
    documentation = (
        "The part of child care subsidy payments that exceeds the bill of the "
        "provider each payment goes to. That provider keeps it, and it pays "
        "none of another provider's bill. Zero for a program modeled with one "
        "payment against the whole family's bill, and never more than the "
        "unit's child care subsidies."
    )
    unit = USD

    def formula(spm_unit, period, parameters):
        above_bills = add(spm_unit, period, ["vt_ccfap_payment_above_bill"])
        paid = add(spm_unit, period, ["vt_ccfap_child_payment"])
        subsidies = spm_unit("child_care_subsidies", period)
        # These payments make up part of child_care_subsidies. When a reform or
        # input sets the subsidy apart from the modeled payments, it pays the
        # providers' bills first, and only what it leaves after the part of
        # the modeled payments that went to bills counts as above them. A
        # subsidy of zero leaves nothing above.
        return max_(min_(subsidies - (paid - above_bills), above_bills), 0)
