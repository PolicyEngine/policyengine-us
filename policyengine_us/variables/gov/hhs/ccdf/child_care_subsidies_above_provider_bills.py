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
        # These payments make up part of child_care_subsidies, so a reform or
        # input that removes the subsidy takes them away too.
        return min_(above_bills, spm_unit("child_care_subsidies", period))
