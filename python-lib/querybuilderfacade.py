# -*- coding: utf-8 -*-
import asterqueryutility as queryutility
import cascadequerybuilder as cascadequery
import singlequerybuilder as singlequery
from inputtableinfo import *
from outputtableinfo import *


def getSelectClause(dss_function, inputTables):
    return cascadequery.getSelectQuery(dss_function, inputTables)\
        if 'cascaded_functions' in \
        dss_function else singlequery.getSelectQuery(dss_function, inputTables)

def getCreateQuery(dss_function, inputTables, outputTable):
    return CREATE_QUERY.format(outputTable.tableType,
                       outputTable.tablename,
                       outputTable.hashKey and DISTRIBUTE_BY_HASH.format(outputTable.hashKey),
                       getSelectClause(dss_function, inputTables))

def getDropOutputTableArgumentsStatements(args):
    return ['BEGIN TRANSACTION;'] + [DROP_QUERY.format(outputTablename=x.get('value', ''))\
            for x in args if x.get('isOutputTable', False) and x.get('value','')] + ['COMMIT;']

def getBeginDropCreateQueries(dss_function, inputTables, outputTable):
     return [BEGIN_TRANSACTION_QUERY,
                    DROP_QUERY.format(outputTablename=outputTable.tablename),
                    getCreateQuery(dss_function, inputTables, outputTable),
                    COMMIT_QUERY]

def getFunctionsQuery(dss_function, inputTables, outputTable):
    return getBeginDropCreateQueries(dss_function, inputTables, outputTable)

