from policyengine_us.model_api import *


class wi_cts_other_countable_resources(Variable):
    value_type = float
    entity = Person
    label = "Wisconsin CTS countable resources outside SSI countable resources"
    definition_period = MONTH
    unit = USD
    quantity_type = STOCK
    defined_for = StateCode.WI
    # PDF pages 31-32
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf#page=31"
    documentation = "Handbook 3.2.2 countable assets that SSI countable resources omit, such as the cash value of life insurance, loan proceeds available for living expenses, the equity value of non-home real property, and vehicle equity above the disregarded first $1,500 of one vehicle."
