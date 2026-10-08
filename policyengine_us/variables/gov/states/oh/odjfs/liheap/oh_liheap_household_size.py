from policyengine_us.model_api import *


class oh_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Ohio HEAP household size"
    defined_for = StateCode.OH
    # Sections E-2.1 and E-2.6.
    # PDF pages 7, 10
    reference = "https://irp.cdn-website.com/aa88b0b1/files/uploaded/2022-24%20ATTACHMENT%202022-2023%20EAP%20Guidelines%20%281%29.pdf#page=7"

    # Nonqualified members are excluded from size, but their income counts.
    # SPM membership approximates the energy economic unit. Custody, temporary
    # absences, foster arrangements, and separate roomers need verified facts
    # that the existing inputs do not fully identify.
    adds = ["is_citizen_or_legal_immigrant"]
