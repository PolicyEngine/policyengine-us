from policyengine_us.model_api import *


class ia_basic_deduction_joint(Variable):
    value_type = float
    entity = Person
    label = "Iowa deduction of either standard or itemized deductions when married couples file jointly"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf"
    )
    defined_for = StateCode.IA

    def formula(person, period, parameters):
        """
        FROM THE 2021 INSTRUCTIONS (PAGE 46):
          You may itemize deductions or claim the Iowa standard deduction,
        whichever is larger. You may itemize deductions on your Iowa return
        even if you did not itemize deductions on your federal return.
        """
        return max_(
            person("ia_standard_deduction_joint", period),
            person("ia_itemized_deductions_joint", period),
        )
