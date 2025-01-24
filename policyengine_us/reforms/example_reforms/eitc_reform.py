# policyengine_us/reforms/example_reforms/eitc_reform.py

from policyengine_core.reforms import StructuralReform
from policyengine_us.reforms.example_variables.eitc import eitc

eitc_reform = StructuralReform("gov.contrib.example_parameters.eitc_reform")
eitc_reform.update_variable(eitc)

# Also allowable are the below:
# example_reform.add_variable(eitc) (if it didn't already exist in the tax-benefit system)
# example_reform.neutralize_variable("eitc")
