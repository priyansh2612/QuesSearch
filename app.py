

import math
import re
from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField

# Function to load vocabulary from vocab.txt and idf values from idf-values.txt
def load_vocab():
    vocab = {}
    with open("vocab.txt", "r") as f:
        vocab_terms = f.readlines()
    with open("idf-values.txt", "r") as f:
        idf_values = f.readlines()

    # Creating a dictionary with terms as keys and idf values as values
    for (term, idf_value) in zip(vocab_terms, idf_values):
        vocab[term.rstrip()] = int(idf_value.rstrip())

    return vocab

# Function to load documents from document.txt
def load_document():
    with open("document.txt", "r") as f:
        documents = f.readlines()

    return documents

# Function to load inverted index from inverted_index.txt
# Returns a dictionary with terms as keys and document indexes in which they are present as values
def load_inverted_index():
    inverted_index = {}
    with open('inverted_index.txt', 'r') as f:
        inverted_index_terms = f.readlines()

    for row_num in range(0, len(inverted_index_terms), 2):
        term = inverted_index_terms[row_num].strip()
        documents = inverted_index_terms[row_num+1].strip().split()
        inverted_index[term] = documents

    return inverted_index

# Function to load links from Qindex.txt
def load_link_of_qs():
    with open("Question Scrapper\Qindex.txt", "r") as f:
        links = f.readlines()

    return links

# Function to load headings from index.txt
def load_headings():
    with open("Question Scrapper\index.txt", "r", encoding='utf-8', errors="ignore") as f:
        lines = f.readlines()

    headings = []
    for heading in lines:
        words = heading.split()
        heading = ' '.join(words[1:])
        headings.append(heading)

    return headings

vocab = load_vocab()  # Load vocabulary
document = load_document()  # Load documents
inverted_index = load_inverted_index()  # Load inverted index
Qlink = load_link_of_qs()  # Load links
headings = load_headings()  # Load headings

# Function to calculate the term frequency for a given term in each document
# Returns a dictionary with document indexes as keys and normalized term frequency as values
def get_tf_dict(term):
    tf_dict = {}
    if term in inverted_index:
        for doc in inverted_index[term]:
            if doc not in tf_dict:
                tf_dict[doc] = 1
            else:
                tf_dict[doc] += 1

    for doc in tf_dict:
        # Dividing the frequency of the word in the document by the total number of words in the indexed document
        try:
            tf_dict[doc] /= len(document[int(doc)])
        except (ZeroDivisionError, ValueError, IndexError) as e:
            print(e)
            print("Error in doc: ", doc)

    return tf_dict

# Function to calculate the IDF (Inverse Document Frequency) value for a given term
def get_idf_value(term):
    return math.log((1 + len(document)) / (1 + vocab[term]))

# Function to calculate the sorted order of documents based on query terms
def calc_docs_sorted_order(q_terms):
    potential_docs = {}  # Dictionary to store the documents which can be the answer
    q_Links = []
    
    # Iterating over query terms
    for term in q_terms:
        if term not in vocab:
            continue

        tf_vals_by_docs = get_tf_dict(term)  # Get the term frequency dictionary for the term
        idf_value = get_idf_value(term)  # Get the IDF value for the term

        # Calculating the sum of TF-IDF values for each document
        for doc in tf_vals_by_docs:
            if doc not in potential_docs:
                potential_docs[doc] = tf_vals_by_docs[doc] * idf_value
            else:
                potential_docs[doc] += tf_vals_by_docs[doc] * idf_value

        # Dividing the scores of each document by the number of query terms
        for doc in potential_docs:
            potential_docs[doc] /= len(q_terms)

        # Sort the potential documents in descending order based on the calculated values
        potential_docs = dict(sorted(potential_docs.items(), key=lambda item: item[1], reverse=True))

        # If no matching documents found
        if len(potential_docs) == 0:
            print("No matching question found. Please search with more relevant terms.")

        count = 0
        for doc_index in potential_docs:
            q_Links.append([potential_docs[doc_index],
                            Qlink[int(doc_index) - 1],
                            headings[int(doc_index) - 1]])
            count += 1
            if count > 20:
                break

    q_Links = sorted(q_Links, key=lambda item: item[0], reverse=True)
    q_Links = q_Links[:20]

    ans = []  # List to store the answer [link, heading]
    for link in q_Links:
        ans.append([link[1], link[2]])

    return ans

# Use of Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# Search Form for users to input the query
class Search_Form(FlaskForm):
    search = StringField("Enter your search terms:")
    submit = SubmitField("Search")

# Home route for the web application
@app.route("/", methods=['GET', 'POST'])
def home():
    form = Search_Form()
    ans = []
    q_terms = []
    if form.validate_on_submit():
        query = form.search.data
        q_terms = [term.lower() for term in query.strip().split()]
        ans = calc_docs_sorted_order(q_terms)[:20]

    if len(q_terms) != 0:
        search_triggered = True
    else:
        search_triggered = False

    return render_template('index.html', form=form, results=ans, search_triggered=search_triggered)
