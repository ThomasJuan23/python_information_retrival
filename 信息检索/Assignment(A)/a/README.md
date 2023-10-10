# IR assignment 

## 18206160 Zhao Chenyang

### Overall

There are two python files in these document, and they can be used for large corpus and small corpus respectively.  All of the sections can be implemented by these files,  the only differences between the two files is that the way of implement Bpref. 

### Design decision

The design is not complex. As for how to split words, there are two parts. The first part is dealing with the document, I only remove the stopwords, do stemming and remove the special symbols that appears at the end of term. I do not remove the special symbol that appear in the middle of the terms, because it is not common, and it waste time. However, I remove the special symbol that appear in the middle of the terms for the query, because the query is shorter than documents a lot.

As for how I organize my index, I just store the BM25 score of each term in each document. Although it may need a lot of time when indexing,  the time of querying saved a lot. In addition, we may need to query over and over again after indexing.