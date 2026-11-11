from policyengine_us.model_api import *


class vt_ccfap_assigned_family_share(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.VT
    label = "Vermont CCFAP family share assigned to the child's provider"
    reference = (
        # PDF pages 10, 12
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/Benefits/CCFAP-Family-Booklet.pdf#page=10",
        # Section B(2), effective September 15, 2025
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/CDD.1050-Child-Care-Authorizations-and-Certificates.pdf#page=3",
        # Blended example 5
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/CDD-Memo-UPK-and-CCFAP-family-tuition-Summer-2026-Update.pdf#page=9",
        # Questions 1, 3 and 7
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Understanding-Payments.pdf#page=1",
    )

    def formula(person, period, parameters):
        # The department assigns the family share to the youngest child's
        # certificate first, with any share left over going to the next child
        # (2023/24 family booklet; CDD.1050 B(2) from September 15, 2025;
        # example 5 of the August 2026 memo). CDD.1050 ranks a registered or
        # licensed provider on a fixed schedule ahead of a relative or a
        # variable schedule; every certificate modeled here is of that first
        # kind. No source says how much share one certificate takes before the
        # rest moves on. We take it up to what the state would otherwise pay
        # for the child, the child's rate, because the certificate carries the
        # family share but not what the family owes above the state rate
        # (Understanding Payments, question 7). Since December 17, 2023 that
        # rate is the state rate (questions 1 and 3). Children of the same age
        # take the share in the order the SPM unit lists them.
        rate = person("vt_ccfap_child_rate", period)
        age = person("age", period.this_year)
        order = person.get_rank(person.spm_unit, age, rate > 0)
        remaining = person.spm_unit("vt_ccfap_family_share", period)
        assigned = np.zeros_like(rate)
        for position in range(int(np.max(order, initial=-1)) + 1):
            at_position = order == position
            available = person.spm_unit.sum(where(at_position, rate, 0))
            taken = min_(remaining, available)
            assigned = where(at_position, taken, assigned)
            remaining = remaining - taken
        return assigned
