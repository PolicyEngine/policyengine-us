from policyengine_us.model_api import *


class ia_net_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa net income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf"
    )
    defined_for = StateCode.IA
    adds = ["adjusted_gross_income", "ia_net_income_additions"]
    subtracts = ["ia_net_income_subtractions"]

    """
    FROM THE 2021 INSTRUCTIONS (PAGE 4):
      For tax years beginning on or after January 1, 2020, Iowa has
    adopted rolling conformity, meaning the state will automatically
    conform with any changes made to the Internal Revenue Code (IRC),
    except as specified by Iowa law.
      For the most part, the calculation of Iowa net income is still the
    same as the calculation for federal adjusted gross income
    (AGI). However, the calculation of Iowa net income will be
    different from the federal AGI calculation when it comes to
    certain items described later in these instructions, such as
    depreciation for certain assets placed in service before tax year
    2021, section 179 special election deductions, and the business
    interest expense limitation.
    """
