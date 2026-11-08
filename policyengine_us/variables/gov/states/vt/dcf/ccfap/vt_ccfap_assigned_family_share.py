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
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Understanding-Payments.pdf#page=1",
    )

    def formula(person, period, parameters):
        # In its 2023/24 family booklet, the department has the family pay its
        # share to the youngest child's provider first, with any share left
        # over going to the next provider. Each provider takes the share up to
        # what the state would otherwise pay it for the child, the child's
        # rate, so the share lowers the state's payment dollar for dollar until
        # it runs out. Since December 17, 2023 that rate is the state rate
        # (Understanding Payments, questions 1 and 3). Children of the same age
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
