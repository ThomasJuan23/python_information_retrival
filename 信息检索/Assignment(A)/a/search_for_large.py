import os
import math
import json
from files import porter
import time
import sys

# write the index file at first
def getIndex(stopwords,stemmer): # stopwords and porter need to be pre-processed, p means porter
    filenames = os.listdir('./documents') # get all documents id
    stemmed = {} # key is the term name, value is used to store the term which has been stemmed
    avg_doclen = 0 # It is the average length of a document in the collection
    len_documents = {}  # key is the document id, value is used to Store the length of one document
    frequency = {} # key is the document id, value is also a dictionary,
    # key is the term name, value is used to store the frequency of one query in one document,
    number_of_terms = {}   # key is term name, value is used to store the total number of one term
    for filename in filenames:  # Iterate through each document
        with open('./documents/' + filename, 'r', encoding='utf-8') as f:
            content = f.read().split()
            frequency[filename] = {}    # key is the term name,
                                           # value is used to store the frequency of one query in one document
            term_counter = 0
            for term in content:  # Iterate through each query
                term = term.lower()   #All lowercase letters
                term = term.strip("[]\{}|_+=)-(*&$#!~`':;'?/,.><") #Remove the closing punctuation
                if term not in stopwords:  # remove stopwords
                    if term not in stemmed:  # avoid useless stemming
                        stemmed[term] = stemmer.stem(term)
                    term = stemmed[term]
                    if term not in frequency[filename]:  # store the frequency of the terms in this document
                        if term not in number_of_terms:   # Summarize the number of occurrences of word items
                            number_of_terms[term] = 1
                        else:
                            number_of_terms[term] = number_of_terms[term] + 1
                        frequency[filename][term] = 1
                    else:
                        frequency[filename][term] = frequency[filename][term] + 1
                    term_counter = term_counter + 1    # calculate the length of the document
            len_documents[filename] = term_counter   # store the length of the document
            avg_doclen = avg_doclen + term_counter   # calculate the length of all documents

    avg_doclen = float(avg_doclen / len(filenames))   # calculate the average length of document
    BM25 = {}     # key is document id, value is also a dictionary, key is the name of term, value is the BM25 score

    for documentID in frequency: # get BM25 score of each term in each document
        BM25[documentID] = {} # key is the name of term, value is the BM25 score
        for term in frequency[documentID]:  # calculate BM25 score
            BM25[documentID][term] = (float(frequency[documentID][term]) * 2.0) / (
                    float(frequency[documentID][term]) + 0.25 + (
                    0.75 * float(len_documents[documentID]) / float(avg_doclen))) * math.log2(
                (float(len(frequency)) - (float(number_of_terms[term]) + 0.5)) / (
                        float(number_of_terms[term]) + 0.5))

    with open('./index.txt', 'w') as file:  # write index file using json
        json.dump(BM25, file)

 # query, and return the result set, the result set is a dictionary without order
def querying(queries, stopwords, BM25, type, stemmer):
    stemmed = {}  # key is the term name, value is used to store the term which has been stemmed
    score = {}  # key is document id, value is the BM25 score
    terms = {}  # key is the term name, value is also the term name, it is easy to search
    for term in queries:
        term = term.strip("[]\{}|_+=)-(*&$#!~`':;'?/,.><") # Remove the closing punctuation
        if term not in stopwords:   # remove stopwords
            if term not in stemmed:     # stemming
                stemmed[term] = stemmer.stem(term)
            term = stemmed[term]
            terms[term] = term  # get the formal name of all terms

    for docID in BM25:  # go through each document
        for docterms in BM25[str(docID)]: # calculate the sum of BM25 score of queries in one document
            if docterms in terms:
                if docID not in score:
                    score[docID] = BM25[docID][docterms]
                else:
                    score[docID] = score[docID] + BM25[docID][docterms]
        if type == "user":    # if the querying is used for user, the non-relevance document's score is 0
            if docID not in score:
                score[docID] = 0
    return score   # return result set


def evaluation(stopwords, BM25,stemmer):
    queries = {}  # key is the query id, value is a list which is used to store query
    resultSet = {}  # key is the query id, value is also a dictionary, key is the document id, value is BM25 score
    relavance_of_queries = {}  # key is the query id, value is also a dictionary, key is the document id,
    # value is the relevance
    number_of_relavant = {}  # key is the query id, value is the number of relevant document
    Sum_precisions = 0  # store the sun of precision of all queries
    Sum_recalls = 0  # store the sun of recall of all queries
    Sum_P10s = 0  # store the sun of P@10 of all queries
    Sum_R_precisions = 0  # store the sun of R-precision of all queries
    Sum_MAPS = 0  # store the sun of MAP of all queries
    Sum_bprefs = 0  # store the sun of bpref of all queries
    with open('./files/qrels.txt', 'r') as file: # get the relevant of each document of each query, and calculate
        # the number of relavant document
        relavance_informations = file.readlines()
        for relavance_information in relavance_informations:
            information = relavance_information.split()
            if information[0] not in relavance_of_queries:
                relavance_of_queries[information[0]] = {}
            relavance_of_queries[information[0]][information[2]] = information[3]  # get the relavance of each document
            if information[3] != '0':   # remove the non-relavant document
                if information[0] not in number_of_relavant: # get the number of relavant document
                    number_of_relavant[information[0]] = 1
                else:
                    number_of_relavant[information[0]] = number_of_relavant[information[0]] + 1

    with open('./files/queries.txt', 'r') as f:
        sample_queries = f.readlines()
        for query in sample_queries:
            for i in "[<('":
                query = query.replace(i, "") # Remove special symbols that often appear in term
            words = query.split()
            queries[words[0]] = []
            for word in words:  # get the query list
                if word != words[0]:
                    queries[words[0]].append(word)
            resultSet[words[0]] = querying(queries[words[0]], stopwords, BM25, "evaluation",stemmer)
            # key is the document id, value is BM25 score
            rankList = sorted(resultSet[words[0]], key=resultSet[words[0]].get, reverse=True)
            number_of_relret = 0  # store the number of relavant document in first retrival document
            number = 0  # store the number of document which has been went through
            Sum_MAP = 0  # store MAP before calculated by the number of relavant document
            Sum_bpref = 0  # store bpref before calculated by the number of relevant document
            number_of_nonrel = 0
            for doc in rankList[:50]:   # go through the first 50 result sets
                if doc in relavance_of_queries[words[0]] and relavance_of_queries[words[0]][doc] == '0':
                    # go through the non-relavant document
                    number_of_nonrel = number_of_nonrel + 1   # get the number of non-relavant document
                    if number_of_nonrel > int(number_of_relavant[words[0]]):  # 1-number_of_nonrel / number_of_relavant
                                                                            # can not less than 0
                        number_of_nonrel = number_of_relavant[words[0]]
                if doc in relavance_of_queries[words[0]] and relavance_of_queries[words[0]][doc] != '0': # go through
                    # the relavant document in retrival document, pay attention to
                    # there are non-relevant document in the file
                    number_of_relret = number_of_relret + 1   # counter the number of relavant document in retrival
                    Sum_MAP = Sum_MAP + number_of_relret / (number + 1)  # calculate MAP before calculated
                                                                              # by the number of relavant document
                    Sum_bpref = Sum_bpref + 1 - (number_of_nonrel / number_of_relavant[words[0]])
                    #  # get bpref before calculated by the number of relevant document
                if number == 9:  # get the number of relavant retrival document in the tenth retrival document
                    relret10 = number_of_relret
                if number == number_of_relavant[words[0]] - 1:
                    Rrelret = number_of_relret # get the number of relavant retrival document
                                                   # in the Rth retrival document, R is the number of relavant document
                number = number + 1
            Sum_precisions = Sum_precisions + number_of_relret / 50 # get the precision of one query and add them
            Sum_recalls = Sum_recalls + number_of_relret / number_of_relavant[words[0]]
            # get the recall of one query and add them
            Sum_P10s = Sum_P10s + relret10 / 10
            # get the P@10 of one query and add them
            Sum_R_precisions = Sum_R_precisions + Rrelret / number_of_relavant[words[0]]
            # get the R-precision of one query and add them
            Sum_MAPS = Sum_MAPS + Sum_MAP / number_of_relavant[words[0]]
            # get the MAP of one query and add them
            Sum_bprefs = Sum_bprefs + Sum_bpref / number_of_relavant[words[0]]
            # get the Bpref of one query and add them
    with open('output.txt', 'w') as output:  # write output file
        for query in queries:
            for i in "[<('":
                query = query.replace(i, "")
            words = query.split()
            rankList = sorted(resultSet[words[0]], key=resultSet[words[0]].get, reverse=True)
            rank = 0             # write the first 50 retrieval document to the output file
            for doc in rankList[:50]:
                output.write(words[0] + " " + 'Q0' + " " + doc + " " + str(rank + 1) + " " + str(
                    resultSet[words[0]][doc]) + " " + '18206150\n')
                rank = rank + 1

    print('Evaluation results') # print the result
    print("Precision: " + str(Sum_precisions / len(queries)))
    print("Recall: " + str(Sum_recalls / len(queries)))
    print("P@10: " + str(Sum_P10s / len(queries)))
    print("R-precision: " + str(Sum_R_precisions / len(queries)))
    print("MAP: " + str(Sum_MAPS / len(queries)))
    print("bpref: " + str(Sum_bprefs / len(queries)))
    end=time.process_time()
    print(end-start)


if __name__ == '__main__':
    stemmer = porter.PorterStemmer()  # get porter
    stopwords = set()   # store stopwords
    with open('./files/stopwords.txt', 'r') as f:
        for line in f:
            stopwords.add(line.rstrip())
    try:    # try to open index file, if it does not exit, create it
        with open('index.txt', 'r') as file:
            print('Loading BM25 index from file, please wait')
            BM25 = json.load(file) # read index file
            print('finished')
    except FileNotFoundError:
        start = time.process_time()
        print('Pre-processing....')
        getIndex(stopwords,stemmer) # create index file
        print('Pre-processing has been finished')
        end = time.process_time()
        print('time is ' + str(end - start))
        with open('index.txt', 'r') as file:
            BM25 = json.load(file)   # read index file
    if sys.argv[1] == '-m':  #  create sys path -m
        if sys.argv[2] == 'manual':  #  create sys path of querying
            query = input("Enter query (Enter 'QUIT' to stop querying): \n")
            for i in "[<('": # Remove symbols that often appear in the middle of term
                query = query.replace(i, "")
            query = query.lower()
            while query != "quit":  # loop until the user enter quit
                start = time.process_time()
                if query == "":  # the case of entering nothing
                    print("Please enter query")
                    query = input("Enter query (Enter 'QUIT' to stop querying): \n")
                else:
                    queries = query.split()
                    score = querying(queries, stopwords, BM25, "user",stemmer)   # get the result set
                    rankList = sorted(score, key=score.get, reverse=True)  # sort result set
                    print('Results for query [' + query + ']')   # print the  first fifty result set
                    print("{} {}     {}".format("Rank", "DocumentID", "Similarity score"))
                    rank = 0
                    for doc in rankList[:15]:
                        print("{} {} {}".format(rank + 1, doc, score[doc]))
                        rank = rank + 1
                    end = time.process_time()
                    print("time is " + str(end - start))
                    query = input("Enter query (Enter 'QUIT' to stop querying): \n")
                    # let the user decide if querying again

            else:
                print("Querying is over")
        if sys.argv[2] == 'evaluation': # the evaluation path
            start = time.process_time()
            evaluation(stopwords,BM25,stemmer)

