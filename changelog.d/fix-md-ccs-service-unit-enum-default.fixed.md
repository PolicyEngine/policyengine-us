Gave `md_ccs_service_unit` an explicit `UNIT_1` default so negative or NaN childcare hours resolve to one unit instead of an integer 0 that cannot be encoded as a service unit.
