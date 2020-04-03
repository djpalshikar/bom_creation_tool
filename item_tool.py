#!/usr/bin/python3
import bom_tool
import csv
import time
import os
from multiprocessing import Pool
def increment(index_list,max_list, carry =1):
    tempList = list(index_list)
    #repeat of operation (a+c)/b , carry
    for i in range(len(index_list)-1,-1,-1):
        tmp = tempList[i] + carry
        rem = tmp % max_list[i]
        carry = int(tmp / max_list[i])
        tempList[i] = rem
        if carry == 0:
            break

    return tempList

def generateItemCode(abbr_pos_list, current_item_count, options_list):
    item_code = ''
    error = False
    for i,abbr in zip(range(len(abbr_pos_list)),abbr_pos_list):
        if current_item_count[i] < len(abbr): #normal situation
            #print("abbr[current_item_count[i]]", abbr, " ",current_item_count[i])
            item_code = item_code + abbr[current_item_count[i]] + '-'
        elif ( (current_item_count[i] == len(abbr))\
                and options_list[i]): #check, abbr must be optional if index is == len
            continue
        elif options_list[i]:
            #print("ERROR: out of range with {0}".format(abbr))
            error = True
        else:
            #print("ERROR: compulsory abbr out of range {0}".formar(abbr))
            error = 1

    return [item_code.rstrip('-'), error]

            
def removeOptionalContraintsIndex(current_item_count, max_count_list, row_options):
    newIndexList = []
    row_no = 0

    for i,count in zip(range(len(current_item_count)),current_item_count):
        if not row_options[i]:
            newIndexList.append(row_no + current_item_count[i])
        elif count < (max_count_list[i] - 1):
           #optional row and index is valid
            newIndexList.append(row_no + current_item_count[i])
        row_no  = row_no + (max_count_list[i]-1 if row_options[i] else max_count_list[i])
    return newIndexList 

    
 ## continue from here !1!
def createThreadArgs(max_threads):
    thread_pool=[]
    for i in range(max_threads):
        thread_pool.append([i+1, max_threads])

    return thread_pool
def createItems(item_range):
    item_contraints_dict = csv.DictReader(open("item_constraints.csv"),quoting=csv.QUOTE_NONNUMERIC)
    item_rows = csv.DictReader(open("item_rows.csv"),quoting=csv.QUOTE_NONNUMERIC)
    row_nos =[]
    row_options=[]
    for row in item_rows:
         row_nos.append(int(row['position']))
         row_options.append(bool(row['optional']))


    item_candidate_rows = []
    item_abbr_list = []
    item_must_list = []
    item_none_list = []
    abbr_pos_list = []
    temp = []
    abbr_pos_list.append(temp)

    for row in item_contraints_dict:
        item_candidate_rows.append(int(row['position']))
        item_abbr_list.append(bom_tool.getStr(row['abbr']))
        item_must_list.append(bom_tool.getStr(row['must']))
        item_none_list.append(bom_tool.getStr(row['none']))

    for i in range(len(item_candidate_rows)):
        if len(abbr_pos_list) == (item_candidate_rows[i] - 1):
            abbr_pos_list.append([])

        abbr_pos_list[len(abbr_pos_list)-1].append(item_abbr_list[i]) 

    fileMap = bom_tool.useNewCSVFile('Item','Item_{0}_of_{1}'.format(item_range[0],item_range[1]),['Item'])
    itemWriter = fileMap['writer']
    itemFileDesc = fileMap['fileDesc']

    max_item_count = 1
    max_count_list = []
    for i in range(len(abbr_pos_list)):
        count = (len(abbr_pos_list[i]) + (1 if row_options[i] else 0))
        max_item_count *= count 
        max_count_list.append(count)
        #print( max_item_count)

   # print(max_item_count, ' max item')
   # print(max_count_list)
   
    range_slots = list(range(0,max_item_count, int(max_item_count/item_range[1])))
    #print("range, slots ",range_slots)
    current_item_count = increment([0]*len(max_count_list), max_count_list, \
            range_slots[item_range[0]-1])
    index_max_count =  (range_slots[item_range[0]] - range_slots[item_range[0]-1]) if item_range[0] != item_range[1] \
            else (max_item_count - range_slots[item_range[0]-1])

    print("item range{0}, from {1}, to {2} ,current_item_count{3} ".format(item_range,range_slots[item_range[0]-1] ,\
            range_slots[item_range[0]-1] + index_max_count -1, current_item_count))



    for i in range(index_max_count):
        #print(i)
        #print("current_item_count = {0}".format(current_item_count))
        [item_code, error] = generateItemCode(abbr_pos_list, current_item_count, row_options)
        if not error:
            #check for constraints
            must_constraint = ';'.join(filter(None,[item_must_list[k] for k in  removeOptionalContraintsIndex(current_item_count,max_count_list,row_options)]))#\
#                    [item_abbr_list.index(j) for j in item_code.split('-')]])) # creats str like 'VITAL;I;SCUTE;D'

            none_constraint = ';'.join(filter(None,[item_none_list[k] for k in removeOptionalContraintsIndex(current_item_count,max_count_list,row_options)])) 
                   # [item_abbr_list.index(j) for j in item_code.split('-')]])) # creats str like 'SCUTE;VF100'
            
            #print('must constraint ',must_constraint)
            if bom_tool.mustContain(item_code, must_constraint) and not \
                    bom_tool.bannedPresent(item_code, none_constraint):
                #valid item
                itemWriter.writerow([item_code])
            #else:
                #print("Rejected Item Code ",item_code)

        current_item_count = increment(current_item_count,max_count_list,1)


    itemFileDesc.close()
            





if __name__ == '__main__':
    #change no of threads here
    max_threads = 10
    
    with Pool(max_threads) as p:
        p.map(createItems,createThreadArgs(max_threads))

        



