from policyengine_us.model_api import *


class wi_veterans_property_tax_credit_elected(Variable):
    """This return actually elects or claims the credit for this taxable year.

    Potential eligibility, a positive calculated alternative credit or veteran
    status alone does not establish an actual filed election.
    """

    value_type = bool
    entity = TaxUnit
    label = "Wisconsin veterans property tax credit is claimed"
    definition_period = YEAR
    reference = "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/6e"
