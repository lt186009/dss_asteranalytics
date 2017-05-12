from sets import Set
# -*- coding: utf-8 -*-
import asterqueryutility as queryutility

def getAsterQuery(dss_function, inputTables, outputTable):
    # query
    multipleinputs = ""
    if 'required_input' in dss_function:
        requiredinputs = [x for x in dss_function['required_input'] if 'name' in x and 'value' in x and x['value']]
        inputTable = inputTables[0]
        asterschema = inputTable.tablename.split('.')[0]
        for requiredinput in requiredinputs:
            if 'value' in requiredinput and requiredinput["value"]:
                aliasedinputtableschema = next(x.schemaname for x in inputTables if x.tablenamewithoutschema == requiredinput['value'])
                inputkind = requiredinput['kind']
                partitionKeys = ""
                if 'Dimension' == inputkind:
                    partitionKeys = 'DIMENSION'
                elif "PartitionByAny" == inputkind:
                    partitionKeys = 'PARTITION BY ANY'
                elif "PartitionByKey" == inputkind:
                    partitionKeys = 'PARTITION BY ' + requiredinput['partitionAttributes']
                elif "PartitionByOne" == inputkind:
                    partitionKeys = 'PARTITION BY 1'
                else:
                    partitionKeys = ""
                    
                orderKeys = ""
                if requiredinput['isOrdered'] and requiredinput['orderByColumn']:
                    orderKeys = "ORDER BY " + requiredinput['orderByColumn']
                multipleinputs += """ON {schema}.{input_table} AS {input_name} {partitionKeys} {orderKeys}\n""".format(schema=aliasedinputtableschema,
                                                                                                                       input_table=requiredinput['value'],
                                                                                                                       input_name=requiredinput['name'],
                                                                                                                       partitionKeys=partitionKeys,
                                                                                                                       orderKeys=orderKeys)
    
    if outputTable.tableType is None or outputTable.tableType == '':
        outputTable.tableType = 'DIMENSION'
    
    query = """BEGIN TRANSACTION;
               DROP TABLE IF EXISTS {};
               CREATE {} TABLE {}{}
               AS 
               SELECT *
               FROM   {}
                      (
                     {}   
               {}
               {}
                       {}
               {}
                      ) 
            """.format(outputTable.tablename,
                       outputTable.tableType,
                       outputTable.tablename,
                       " DISTRIBUTE BY HASH({})".format(outputTable.hashKey) if "FACT" == outputTable.tableType else "",
                       dss_function["name"],
                       multipleinputs,
                       "" if (0 == len([x for x in dss_function['required_input'] if 'name' not in x])) else ('ON ' + inputTable.tablename),
                       "" if (0 == len([x for x in dss_function['required_input'] if 'name' not in x])) else ("" if not inputTable.partitionKey else " ".join(["PARTITION BY", inputTable.partitionKey])),
                       "" if (0 == len([x for x in dss_function['required_input'] if 'name' not in x])) else ("" if not inputTable.orderKey else " ".join(["ORDER BY", inputTable.orderKey])),
                       queryutility.getJoinedArgumentsString(dss_function["arguments"]))   

       
    query +=""";
           COMMIT;
           END TRANSACTION;
        """
        
    return query