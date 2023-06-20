import os
import re
import chardet

#get file path to data 
#file_path = os.path.dirname(os.path.abspath('E:\projects summer 2023\TF IDF\Question Scrapper\data)'))


data_folder='Question Scrapper\data'

lines=[] #contains a list of lines, each line contiasn content of the question
for i in range(1,2406)  :
    file_path=os.path.join(data_folder, "{}/{}.txt".format(i, i))

    temp=" "
    with open(file_path,'r', encoding= 'utf-8', errors = "ignore") as f:
        text=f.readlines()
    
    for line in text:
        if "Example" in line:
            break;
        else:
            temp+=line
    
    lines.append(temp)


def preprocess(filename): #remove problem number and lowercase words
    #remove alphanumeric characters
    filename = re.sub(r'[^a-zA-Z0-9]', ' ', filename)
    
     #lowercse, remove whitespace,split the string int o a list of substrings with at whitespace,tabs,newline characters, alsp strip
    
    terms = [term.lower() for term in filename.strip().split()]

    return terms



vocab={}
documents = []  


for (index, line)  in enumerate(lines):
    tokens = preprocess(line)       #list of processed words of this doc
    documents.append(tokens)        #list of processes words questions across all the questions 

    tokens = set(tokens)
    for token in tokens:
        if token not in vocab:
            vocab[token] = 1
        else:
            vocab[token] += 1

#reverse sort vocab by values (by the no of docs the word is present in)
vocab = dict( sorted(vocab.items(), key = lambda item : item[1], reverse = True) )


print("No of documents : ", len(documents))
print("Size of vocab : ", len(vocab))
#print("Sample document: ", documents[10])
    


with open("vocab.txt", "w", encoding = 'utf-8', errors = "ignore") as f:
    for key in vocab.keys():
        f.write("%s\n" % key)

# save idf values
with open("idf-values.txt", "w", encoding = 'utf-8', errors = "ignore") as f:
    for key in vocab.keys():
        f.write("%s\n" % vocab[key])


#save the documents(lists of words for each doc)
with open("document.txt", "w", encoding = 'utf-8', errors = "ignore") as f:
    for doc in documents:
        f.write("%s\n" % doc)

inverted_index = {}         # word : list of index of docs the word is present in.
                    # inserting word multiple times from same doc too, so that we even get the term freq from here itself
for (index, doc) in enumerate(documents, start = 1):
    for token in doc:
        if token not in inverted_index:
            inverted_index[token] = [index]
        else:
            inverted_index[token].append(index)



# save the inverted index in a file
with open("inverted_index.txt", 'w', encoding = 'utf-8', errors = "ignore") as f:
    for key in inverted_index.keys():
        f.write("%s\n" % key)
        
        doc_indexes = ' '.join([str(term) for term in inverted_index[key]])
        f.write("%s\n" % doc_indexes)

