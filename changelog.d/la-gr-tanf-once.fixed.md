Count the SPM unit's CalWORKs (tanf) once in Los Angeles County General Relief gross income instead of once per member.

The public `la_general_relief_gross_income` variable moves from Person to SPMUnit. Callers supplying it must move the input from `people` to `spm_units`; direct calculations now return one value per SPM unit instead of one per person.

Break the circular housing subsidy and rent contribution calculation reached when corrected income permits housing assistance. Calculated housing payments use the prescribed contribution schedule; directly supplied rent contribution amounts no longer change the calculated housing subsidy.
