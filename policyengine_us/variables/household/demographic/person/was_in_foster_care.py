from policyengine_us.model_api import *


class was_in_foster_care(Variable):
    value_type = bool
    entity = Person
    label = "Person was previously in a qualifying foster care institution"
    documentation = (
        "Defaults to true when the person is in foster care "
        "(is_in_foster_care) in any month of the year. Set it directly for "
        "a former foster youth who has left care."
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        # A person in foster care during the year has been in foster care.
        # Each former-foster-youth rule applies its own age test, and the
        # reverse cannot be inferred: someone who aged out is not in care now.
        # is_in_foster_care is a monthly flag. Read each month, since an annual
        # read of a monthly boolean returns the December value only.
        return np.any(
            [
                person("is_in_foster_care", month)
                for month in period.get_subperiods(MONTH)
            ],
            axis=0,
        )
