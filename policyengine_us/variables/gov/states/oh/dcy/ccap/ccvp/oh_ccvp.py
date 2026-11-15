from policyengine_us.model_api import *


class oh_ccvp(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Ohio Child Care Choice Voucher Program monthly payment"
    definition_period = MONTH
    defined_for = "oh_ccvp_eligible"
    reference = (
        # PDF pages 2, 4
        "https://dam.assets.ohio.gov/image/upload/childrenandyouth.ohio.gov/For%20Partners/Rules%20and%20Resources/2025/PL_36.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        # Procedure Letter 36: the voucher pays one program per child each
        # month, and that payment plus the family's portion may not exceed the
        # provider's private rate, so the charge caps the payment. The voucher
        # has no Publicly Funded Child Care copayment; the letter encourages
        # programs to hold the family's portion to 9% of income without
        # requiring it. The model leaves out the letter's initial enrollment
        # payment, which programs receive on authorization on top of the
        # monthly payments.
        person = spm_unit.members
        rate = person("oh_ccvp_rate", period)
        charge = person("pre_subsidy_childcare_expenses", period)
        return spm_unit.sum(min_(rate, charge))
