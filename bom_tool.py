#!/usr/bin/python3
import csv
import re
import time
import os
import subprocess
    
def mustContain(item_code, must):
    #returns true if ALL of the abbr are found in item code
    if len(must) <= 0:
        return True
    must_list = must.split(';')
    result = True

    for abbr in must_list:
        result = result and ((re.compile("^{0}-|-{0}-|-{0}$".format(abbr)).search(item_code)) \
                is not None) # checks abbreviations in item code, all must be present

    return result

def bannedPresent(item_code, none):
    #returns true if any none of the abbr are found in item code
    if len(none) <= 0:
       return False
    none_list = none.split(';')
    for abbr in none_list:
        result = ((re.compile("^{0}-|-{0}-|-{0}$".format(abbr)).search(item_code)) \
               is not None) # checks abbreviations in item code,
        if result:
            break
    return result


def checkMissingRows(current_item, newBom_rows, row_options):
    all_rows = set(range(1,len(row_options)))
    present_rows = set(newBom_rows)
    missing_rows = list(all_rows - present_rows)
    for i in missing_rows:
        if not row_options[i-1]:
            print("error: missing compulsory bom row at pos {0} for item {1}, continuing".format(i,current_item))

def useNewCSVFile(dirName,namePrefix,header):
    if dirName not in os.listdir('.'):
        os.mkdir(dirName)

    outFileName = '{4}/auto{5}_{2}_{1}_{0}_{3}.csv'.format(time.localtime().tm_year,\
            time.localtime().tm_mon,time.localtime().tm_mday,int(time.time()),dirName,namePrefix)
    bomFileDesc = open(outFileName,'w+',buffering=1)
    bomWriter = csv.writer(bomFileDesc,quoting=csv.QUOTE_NONNUMERIC)
    bomWriter.writerow(header) #write header 
    return {'writer':bomWriter, 'fileDesc':bomFileDesc}

def getStr(data):
    tp = type(data)
    if tp == type(1.0):
        return str(round(data))
    else:
        return data
         

   
def createBoms(maxLines=4000):
    #reading constraints
    bom_contraints_dict = csv.DictReader(open("bom_constraints.csv"),quoting=csv.QUOTE_NONNUMERIC)
    print("Importing BOM Contraints")
    bom_rows = csv.DictReader(open("bom_rows.csv"),quoting=csv.QUOTE_NONNUMERIC)
    print("Importing bom_rows.csv")

    row_nos =[]
    row_options=[]
    for row in bom_rows:
         row_nos.append(int(row['row_no']))
         row_options.append(bool(row['optional']))


    bom_candidate_rows = []
    bom_msub_list = []
    bom_must_list = []
    bom_none_list = []

    for row in bom_contraints_dict:
        bom_candidate_rows.append(int(row['row_no']))
        bom_msub_list.append(row['bom_item'])
        bom_must_list.append(getStr(row['must']))
        bom_none_list.append(getStr(row['none']))
	
    # creating bom from item_code
    current_item = "VITAL-I-SCUTE-PCPG13-D-U-FS-MB15MS-VF130-HB-10T-1.45H"
    newBom_rows =[] #rows for whic bom has been decided
    newBom_msub =[]
    dirName = 'BOM_auto_output'
    #if dirName not in os.listdir('.'):
    #    os.mkdir(dirName)

    #outFileName = '{4}/autoBOM_{2}_{1}_{0}_{3}.csv'.format(time.localtime().tm_year,\
    #        time.localtime().tm_mon,time.localtime().tm_mday,int(time.time()),dirName)
    #bomFileDesc = open(outFileName,'w',buffering=1)
    #bomWriter = csv.writer(bomFileDesc,quoting=csv.QUOTE_NONNUMERIC)
    fileMap = useNewCSVFile(dirName,'BOM',['item','bom_item'])
    bomWriter = fileMap['writer']
    bomFileDesc = fileMap['fileDesc']
    

   #newBom_qty
    #iterating on items
    item_count = 0
    with open("Item.csv") as itemFile:
            itemReader = csv.reader(itemFile,quoting=csv.QUOTE_NONNUMERIC)
            for current_tuple in itemReader:
                current_item = current_tuple[0]
                item_count += 1
                if current_item == 'Item':
                    continue
         
                for i in range(len(bom_candidate_rows)):
                    #print(i, mustContain(current_item, bom_must_list[i]))
                    mustResult = mustContain(current_item, bom_must_list[i])
                    bannedResult = bannedPresent(current_item, bom_none_list[i])
                    newBomRowNo = len(newBom_msub)

                    if (mustResult and not bannedResult):
                        if bom_candidate_rows[i] >=  (newBomRowNo + 1) :
                            newBom_msub.append(bom_msub_list[i])
                            newBom_rows.append(bom_candidate_rows[i])
                            #print("accepted candidate row".format(bom_candidate_rows[i]))
                            bomWriter.writerow([(current_item if newBomRowNo == 0 else '' ), bom_msub_list[i]])
                        elif bom_candidate_rows[i] < (newBomRowNo + 1) :
                            print('error: Clash detected for item {0}, for bom row pos: {1}, quiting!'.format(\
                                    current_item, bom_candidate_rows[i]))
                            exit()

                checkMissingRows(current_item, newBom_rows, row_options) 
                newBom_msub.clear()
                newBom_rows.clear()
                bomFileDesc.seek(0)
                if bomFileDesc.read().count('\n') >= maxLines:
                    bomFileDesc.close();
                    fileMap = useNewCSVFile(dirName,'BOM_item_row_{}'.format(item_count+1),['item','bom_item'])
                    bomWriter = fileMap['writer']
                    bomFileDesc = fileMap['fileDesc']
    

                        

    if bomFileDesc is not None :
        bomFileDesc.close()


if __name__ == '__main__':
    createBoms(5000)
