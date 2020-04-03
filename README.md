
Automatic item code working
Follow this sequence to create automatic BOM

Step 1: Prepare Files
	Sample files have been provided
	DO NOT change column name or column sequence, or file name
	
	Item.csv 
	single column, cell text should be quoted i.e. when opened in text editor each item should have "" around it.
	
	bom_constraints.csv
	Row_no: It is not unique and can be same. only one sub-assembly from the set of all Sub-assemblies with same row number will be selected for creating bom
		* Row_no should appear in sequence 1,1,2,2,2,3, ,,etc and not like 1,2,1,1.. etc
		
	bom_item
	list all sub-assblies and raw-materials here
	
	
	
	
