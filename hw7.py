import streamlit as st
import re
from collections import Counter

def words(text): return re.findall(r'\w+', text.lower())

WORDS = Counter(words(open('big.txt').read()))

def P(word, N=sum(WORDS.values())): 
    "Probability of `word`."
    return WORDS[word] / N

def correction(word): 
    ori_word_sound = soundex(word)
    candidate_w_and_s = [[word_sound,soundex(word_sound)] for word_sound in candidates(word)]
    candidate_words = [w_and_s[0] for w_and_s in candidate_w_and_s]
    candidate_sounds = [w_and_s[1] for w_and_s in candidate_w_and_s]
    similar_list = []
    
    for candidate_sound in candidate_sounds:
        similarity = 0 #for check similarity between ori_word and candidate word
        for no in range(3): #length of soundex ==3
            if ori_word_sound[no] == candidate_sound[no]:
                similarity += 1
        similar_list.append(similarity)
    
    max_inds = [i for i, x in enumerate(similar_list) if x == max(similar_list)]
    new_candidate_words = [candidate_words[w] for w in range(len(candidate_words)) if w in max_inds]
    
    
    return max(new_candidate_words, key=P)

def candidates(word): 
    "Generate possible spelling corrections for word."
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])


def known(words): 
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word): 
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))


def soundex(query: str):
    """
    https://en.wikipedia.org/wiki/Soundex
    :param query:
    :return:
    """

    # Step 0: Clean up the query string
    query = query.lower()
    letters = [char for char in query if char.isalpha()]

    # Step 1: Save the first letter. Remove all occurrences of a, e, i, o, u, y, h, w.

    # If query contains only 1 letter, return query+"000" (Refer step 5)
    if len(query) == 1:
        return query + "000"

    to_remove = ('a', 'e', 'i', 'o', 'u', 'y', 'h', 'w')

    first_letter = letters[0]
    letters = letters[1:]
    letters = [char for char in letters if char not in to_remove]

    if len(letters) == 0:
        #return first_letter + "000"
        return "000"

    # Step 2: Replace all consonants (include the first letter) with digits according to rules

    to_replace = {('b', 'f', 'p', 'v'): 1, ('c', 'g', 'j', 'k', 'q', 's', 'x', 'z'): 2,
                  ('d', 't'): 3, ('l',): 4, ('m', 'n'): 5, ('r',): 6}

    first_letter = [value if first_letter else first_letter for group, value in to_replace.items()
                    if first_letter in group]
    letters = [value if char else char
               for char in letters
               for group, value in to_replace.items()
               if char in group]

    # Step 3: Replace all adjacent same digits with one digit.
    letters = [char for ind, char in enumerate(letters)
               if (ind == len(letters) - 1 or (ind+1 < len(letters) and char != letters[ind+1]))]

    # Step 4: If the saved letter’s digit is the same the resulting first digit, remove the digit (keep the letter)
    if first_letter == letters[0]:
        letters[0] = query[0]
    else:
        letters.insert(0, query[0])

    # Step 5: Append 3 zeros if result contains less than 3 digits.
    # Remove all except first letter and 3 digits after it.

    first_letter = letters[0]
    letters = letters[1:]
    
#G    first_letter = letters[0]
#G    letters = letters[1:]

    
    letters = [char for char in letters if isinstance(char, int)][0:3]

    while len(letters) < 3:
        letters.append(0)

    #G letters.insert(0, first_letter)

    string = "".join([str(l) for l in letters])

    return string

random_words = ["","apple","lamon","spelling","hapy","language","greay","pig",
                "fest","constitution","werker","sanctuary","drametic","fuss",
                "fame","damaga","glasses","registration","designe","convenience",
                "hypnothize","muscle","drama"]


with st.sidebar:
    check=st.checkbox("Show original word")
select_token = st.selectbox("Choose a word or..",random_words)
text_token = st.text_input("type your own!!",select_token)
if text_token:
    correct_word = correction(text_token)
    if check==True:
        st.markdown(f"Original word: {text_token}")
    if correct_word == text_token:
        st.success(f"{text_token} is the correct spelling!!")
    else:
        st.error(f"Correction:{correct_word}")
