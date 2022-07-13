## md_refunds_of_advanced_tuition_payments_addition.py
from openfisca_us.model_api import *

class md_refunds_of_advanced_tuition_payments_addition(Variable):
    # k. Any refunds of advanced tuition payments made under the Maryland Prepaid College Trust, to the extent the payments were subtracted from federal adjusted gross income and were not used for qualified higher education expenses, and any refunds of contributions made under the Maryland College Investment Plan, to the extent the contributions were subtracted from federal adjusted gross income and were not used for qualified higher education expenses. See Administrative Release 32.
    value_type = float
    entity = TaxUnit
    label = "MD refunds of advanced tuition payments"
    documentation = "Any refunds of advanced tuition payments made under the Maryland Prepaid College Trust, to the extent the payments were subtracted from federal adjusted gross income and were not used for qualified higher education expenses, and any refunds of contributions made under the Maryland College Investment Plan, to the extent the contributions were subtracted from federal adjusted gross income and were not used for qualified higher education expenses. See Administrative Release 32."
    unit = USD
    definition_period = YEAR