import re

def tokenize(doc: str):
    """
    Splits doc into individual tokens
    """
    return filter(lambda x: x != '', re.split('[^a-zA-Z0-9]', re.sub(' +', ' ', doc.lower())))


def convert_tokens_to_ids(tokens, lexicon):
    token_ids = []
    for token in tokens:
        if token in lexicon:
            token_ids.append(lexicon[token])
        else:
            id = lexicon['_tokens']
            lexicon['_tokens'] = id + 1
            lexicon[token] = id
            token_ids.append(id)
    return token_ids

def count_words(token_ids):
    word_count = {}
    for token_id in token_ids:
        if token_id in word_count:
            word_count[token_id] += 1
        else:
            word_count[token_id] = 1
    return word_count

def add_to_postings(word_counts, docid, invindex):
    for term_id in word_counts:
        count = word_counts[term_id]
        invindex.add_doc_word(docid, term_id, count)

def remove_tags(text: str):
    """
    Remove tags from text, can be used to prevent tokenizer from considering words inside tags as a token
    """
    return re.sub('</?[a-zA-Z]*>', '', text)