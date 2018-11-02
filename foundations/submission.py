import collections
import math

############################################################
# Problem 3a

def findAlphabeticallyLastWord(text):
    """
    Given a string |text|, return the word in |text| that comes last
    alphabetically (that is, the word that would appear last in a dictionary).
    A word is defined by a maximal sequence of characters without whitespaces.
    You might find max() and list comprehensions handy here.
    """
    # BEGIN_YOUR_CODE (our solution is 1 line of code, but don't worry if you deviate from this)
    return max((text.split()))
    # END_YOUR_CODE

############################################################
# Problem 3b

def euclideanDistance(loc1, loc2):
    """
    Return the Euclidean distance between two locations, where the locations
    are pairs of numbers (e.g., (3, 5)).
    """
    # BEGIN_YOUR_CODE (our solution is 1 line of code, but don't worry if you deviate from this)
    return math.sqrt(sum([(x-y)**2 for x,y in zip(loc1,loc2)]))
    # END_YOUR_CODE

############################################################
# Problem 3c

def mutateSentences(sentence):
    """
    Given a sentence (sequence of words), return a list of all "similar"
    sentences.
    We define a sentence to be similar to the original sentence if
      - it as the same number of words, and
      - each pair of adjacent words in the new sentence also occurs in the original sentence
        (the words within each pair should appear in the same order in the output sentence
         as they did in the orignal sentence.)
    Notes:
      - The order of the sentences you output doesn't matter.
      - You must not output duplicates.
      - Your generated sentence can use a word in the original sentence more than
        once.
    Example:
      - Input: 'the cat and the mouse'
      - Output: ['and the cat and the', 'the cat and the mouse', 'the cat and the cat', 'cat and the cat and']
                (reordered versions of this list are allowed)
    """
    # BEGIN_YOUR_CODE (our solution is 20 lines of code, but don't worry if you deviate from this)
    cache={}
    words=sentence.split()
    pairs=collections.defaultdict(list)
    for i in range(len(words)-1):
        pairs[words[i]].append(words[i+1])
    def recurse(sentence_length,built_sentence,depth):
        temp=built_sentence.split()
        #if sentence_length<len(temp)+1:return
        if sentence_length==len(temp)+1:
            for w in pairs[temp[-1]]:
                cache[built_sentence+' '+w]=1.0
            return
        if temp[-1] in pairs:
            for word in pairs[temp[-1]]:
                recurse(sentence_length,built_sentence+' '+word,depth+1)
    for item in list(pairs):
        recurse(len(words),item,2)
    return cache.keys()
    # END_YOUR_CODE

############################################################
# Problem 3d

def sparseVectorDotProduct(v1, v2):
    """
    Given two sparse vectors |v1| and |v2|, each represented as collection.defaultdict(float), return
    their dot product.
    You might find it useful to use sum() and a list comprehension.
    This function will be useful later for linear classifiers.
    """
    # BEGIN_YOUR_CODE (our solution is 4 lines of code, but don't worry if you deviate from this)
    return sum([(v1[item]*v2[item]) for item in v1 if item in v2])
    # END_YOUR_CODE

############################################################
# Problem 3e

def incrementSparseVector(v1, scale, v2):
    """
    Given two sparse vectors |v1| and |v2|, perform v1 += scale * v2.
    This function will be useful later for linear classifiers.
    """
    # BEGIN_YOUR_CODE (our solution is 2 lines of code, but don't worry if you deviate from this)
    #print(item for item in v2)
    for item in v2:
        v1[item]+=scale*v2[item]
    return v1
    # END_YOUR_CODE

############################################################
# Problem 3f

def findSingletonWords(text):
    """
    Splits the string |text| by whitespace and returns the set of words that
    occur exactly once.
    You might find it useful to use collections.defaultdict(int).
    """
    # BEGIN_YOUR_CODE (our solution is 4 lines of code, but don't worry if you deviate from this)
    word_count=collections.defaultdict(int)
    for word in text.split():
        word_count[word]+=1
    return set([word for word,count in word_count.items() if count==1])
    # END_YOUR_CODE

############################################################
# Problem 3g

def computeLongestPalindromeLength(text):
    """
    A palindrome is a string that is equal to its reverse (e.g., 'ana').
    Compute the length of the longest palindrome that can be obtained by deleting
    letters from |text|.
    For example: the longest palindrome in 'animal' is 'ama'.
    Your algorithm should run in O(len(text)^2) time.
    You should first define a recurrence before you start coding.
    """
    # BEGIN_YOUR_CODE (our solution is 19 lines of code, but don't worry if you deviate from this)
    n=len(text)
    if n<=1:
        return n
    cache={}
    for i in range(len(text)):
        cache[text[i]]=1
    def getLongestLength(i,j):
        #if single character, return 1
        if i==j:
            return 1
        #if last 2 characters, and the same then return 2
        elif (text[i]==text[j] and (j==i+1)):
            return 2
        #if first and last character are the same, then get longest palindrome of subtext and add 2
        elif text[i]==text[j]:
            string1=text[i+1:j]
            if string1 in cache:
                cost1=cache[string1]
            else:
                cost1=getLongestLength(i+1,j-1)
                cache[string1]=cost1
            return cost1+2
        #if first and last character not the same, split the word into all except last character, and 2nd character to end
        #and run longestlength of each and take the max
        else:
            string1=text[i:j]
            string2=text[i+1:j+1]
            if string1 in cache:
                cost1=cache[string1]
            else:
                cost1=getLongestLength(i,j-1)
                cache[string1]=cost1
            if string2 in cache:
                cost2=cache[string2]
            else:
                cost2=getLongestLength(i+1,j)
                cache[string2]=cost2
            maxcost=max(cost1,cost2)
            return maxcost

    maxLen=getLongestLength(0,len(text)-1)
    return maxLen
    # END_YOUR_CODE
