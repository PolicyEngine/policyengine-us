from policyengine_us.model_api import *


class vt_ccfap_payment_above_bill(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VT
    label = "Vermont CCFAP payment above the bill of the child's provider"
    documentation = (
        "The part of the state's yearly payment to the person's child care "
        "provider that exceeds what the provider charges for the person. The "
        "provider keeps it, so it pays none of the family's bills elsewhere."
    )
    reference = (
        # PDF pages 1, 2, 7 and 10
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/CDD-Memo-UPK-and-CCFAP-family-tuition-Summer-2026-Update.pdf#page=1",
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Understanding-Payments.pdf#page=1",
    )

    def formula(person, period, parameters):
        # Vermont's Child Development Division pays each provider for the
        # child it serves, and a provider's invoice takes only its own
        # payments off its own tuition, so a payment above one provider's
        # tuition can't lower another provider's bill.
        payment = add(person, period, ["vt_ccfap_child_payment"])
        bill = add(person, period, ["vt_ccfap_child_bill"])
        # With no bill recorded, the providers' charges are unknown, so no
        # payment counts as above them.
        unit_bill = person.spm_unit.sum(
            person("pre_subsidy_childcare_expenses", period)
        )
        return where(unit_bill > 0, max_(payment - bill, 0), 0)
