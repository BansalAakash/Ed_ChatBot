from firebase import firebase
import socket
import json
import time
import os
import logging
import glob
from textblob.sentiments import NaiveBayesAnalyzer
from textblob.classifiers import NaiveBayesClassifier
from textblob import TextBlob
import numpy as np
import nltk
import random
import datetime
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import state_union
from nltk.tokenize import PunktSentenceTokenizer
import webbrowser
from dateutil import parser
from nltk.grammar import DependencyGrammar
from nltk.parse import(
DependencyGraph,
ProjectiveDependencyParser,
NonprojectiveDependencyParser,
)
from recommendation_data import dataset
from datetime import datetime, timedelta



from math import sqrt



def similarity_score(person1,person2):

	

	# Returns ratio Euclidean distance score of person1 and person2 



	both_viewed = {}		# To get both rated items by person1 and person2



	for item in dataset[person1]:

		if item in dataset[person2]:

			both_viewed[item] = 1



		# Conditions to check they both have an common rating items	

		if len(both_viewed) == 0:

			return 0



		# Finding Euclidean distance 

		sum_of_eclidean_distance = []	



		for item in dataset[person1]:

			if item in dataset[person2]:

				sum_of_eclidean_distance.append(pow(dataset[person1][item] - dataset[person2][item],2))

		sum_of_eclidean_distance = sum(sum_of_eclidean_distance)



		return 1/(1+sqrt(sum_of_eclidean_distance))







def pearson_correlation(person1,person2):



	# To get both rated items

	both_rated = {}

	for item in dataset[person1]:

		if item in dataset[person2]:

			both_rated[item] = 1



	number_of_ratings = len(both_rated)		

	

	# Checking for number of ratings in common

	if number_of_ratings == 0:

		return 0



	# Add up all the preferences of each user

	person1_preferences_sum = sum([dataset[person1][item] for item in both_rated])

	person2_preferences_sum = sum([dataset[person2][item] for item in both_rated])



	# Sum up the squares of preferences of each user

	person1_square_preferences_sum = sum([pow(dataset[person1][item],2) for item in both_rated])

	person2_square_preferences_sum = sum([pow(dataset[person2][item],2) for item in both_rated])



	# Sum up the product value of both preferences for each item

	product_sum_of_both_users = sum([dataset[person1][item] * dataset[person2][item] for item in both_rated])



	# Calculate the pearson score

	numerator_value = product_sum_of_both_users - (person1_preferences_sum*person2_preferences_sum/number_of_ratings)

	denominator_value = sqrt((person1_square_preferences_sum - pow(person1_preferences_sum,2)/number_of_ratings) * (person2_square_preferences_sum -pow(person2_preferences_sum,2)/number_of_ratings))

	if denominator_value == 0:

		return 0

	else:

		r = numerator_value/denominator_value

		return r 



def most_similar_users(person,number_of_users):

	# returns the number_of_users (similar persons) for a given specific person.

	scores = [(pearson_correlation(person,other_person),other_person) for other_person in dataset if  other_person != person ]

	

	# Sort the similar persons so that highest scores person will appear at the first

	scores.sort()

	scores.reverse()

	return scores[0:number_of_users]



def user_reommendations(person):



	# Gets recommendations for a person by using a weighted average of every other user's rankings

	totals = {}

	simSums = {}

	rankings_list =[]

	for other in dataset:

		# don't compare me to myself

		if other == person:

			continue

		sim = pearson_correlation(person,other)

		#print ">>>>>>>",sim



		# ignore scores of zero or lower

		if sim <=0: 

			continue

		for item in dataset[other]:



			# only score movies i haven't seen yet

			if item not in dataset[person] or dataset[person][item] == 0:



			# Similrity * score

				totals.setdefault(item,0)

				totals[item] += dataset[other][item]* sim

				# sum of similarities

				simSums.setdefault(item,0)

				simSums[item]+= sim



		# Create the normalized list



	rankings = [(total/simSums[item],item) for item,total in totals.items()]

	rankings.sort()

	rankings.reverse()

	# returns the recommended items

	recommendataions_list = [recommend_item for score,recommend_item in rankings]

	return recommendataions_list

		









logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)
GREETING_KEYWORDS = ("hello", "hi", "greetings", "sup", "what's up","good morning","good afternoon","goodevening")

GREETING_RESPONSES = ["'sup bro", "hey", "nice to meet you, how may i assist ?", "hey you get my snap?","Hello ! How are you ?","That's cool","I hear you "]
NONE_RESPONSES=["here is something for you"," i didn't quite get you...but still i tried","excuse me...is this what you want","i am sorry if i got it wrong"," great let me try"," "]
def check_for_greeting(text):
    """If any of the words in the user's input was a greeting, return a greeting response"""
    #sentence=TextBlob(text)
    for word in text.words:
        if word.lower() in GREETING_KEYWORDS:
            return random.choice(GREETING_RESPONSES)



def respond(sentence):
    """Parse the user's inbound sentence and find candidate terms that make up a best-fit response"""
    #cleaned = preprocess_text(sentence)
    parsed = TextBlob(sentence)

    # Loop through all the sentences, if more than one. This will help extract the most relevant
    # response text even across multiple sentences (for example if there was no obvious direct noun
    # in one sentence
    pronoun, noun, adjective, verb = find_candidate_parts_of_speech(parsed)

    # If we said something about the bot and used some kind of direct noun, construct the
    # sentence around that, discarding the other candidates
    resp = check_for_comment_about_bot(pronoun, noun, adjective)

    # If we just greeted the bot, we'll use a return greeting
    if not resp:
        resp = check_for_greeting(parsed)

    if not resp:
        # If we didn't override the final sentence, try to construct a new one:
        if not pronoun:
            resp = random.choice(NONE_RESPONSES)
        elif pronoun == 'I' and not verb:
            resp = random.choice(COMMENTS_ABOUT_SELF)
        else:
            resp = construct_response(pronoun, noun, verb)

    # If we got through all that with nothing, use a random response
    if not resp:
        resp = random.choice(NONE_RESPONSES)

    logger.info("Returning phrase '%s'", resp)
    # Check that we're not going to say anything obviously offensive
    #filter_response(resp)

    return resp

def find_candidate_parts_of_speech(parsed):
    """Given a parsed input, find the best pronoun, direct noun, adjective, and verb to match their input.
    Returns a tuple of pronoun, noun, adjective, verb any of which may be None if there was no good match"""
    pronoun = None
    noun = None
    adjective = None
    verb = None
    
    for sent in parsed.sentences:
        pronoun = find_pronoun(sent)
        noun = find_noun(sent)
        adjective = find_adjective(sent)
        verb = find_verb(sent)
    logger.info("Pronoun=%s, noun=%s, adjective=%s, verb=%s", pronoun, noun, adjective, verb)
    return pronoun, noun, adjective, verb


def find_pronoun(sent):
    """Given a sentence, find a preferred pronoun to respond with. Returns None if no candidate
    pronoun is found in the input"""
    pronoun = None

    for word, part_of_speech in sent.pos_tags:
        # Disambiguate pronouns
        if part_of_speech == 'PRP' and word.lower() == 'you':
            pronoun = 'I'
        elif part_of_speech == 'PRP' and word.lower() == 'i':
            # If the user mentioned themselves, then they will definitely be the pronoun
            pronoun = 'You'
        elif part_of_speech == 'PRP' and word.lower() == 'we':
            # If the user mentioned themselves, then they will definitely be the pronoun
            pronoun = 'You all'
        elif part_of_speech == 'PRP' and word.lower() == 'they':
            # If the user mentioned themselves, then they will definitely be the pronoun
            pronoun = 'They'
        elif part_of_speech == 'PRP' and word.lower() == 'he':
            # If the user mentioned themselves, then they will definitely be the pronoun
            pronoun = 'He'
        elif part_of_speech == 'PRP' and word.lower() == 'she':
            # If the user mentioned themselves, then they will definitely be the pronoun
            pronoun = 'She'
        elif part_of_speech == 'PRP' and word.lower() == 'ourself':
            # If the user mentioned themselves, then they will definitely be the pronoun
            pronoun = 'Yourself'
        elif part_of_speech == 'PRP' and word == 'I':
            # If the user mentioned themselves, then they will definitely be the pronoun
            pronoun = 'You'

    return pronoun

def find_noun(sent):
	noun=None
	
	for word, part_of_speech in sent.pos_tags:
		if part_of_speech =='NN':
			noun=word
	return noun

def find_adjective(sent):
	adjective=None
	for word, part_of_speech in sent.pos_tags:
		if part_of_speech=='JJ':
			adjective=word
	return adjective

def find_verb(sent):
	verb=None
	for word, part_of_speech in sent.pos_tags:
		if part_of_speech=='VBZ' or part_of_speech=='VB' or part_of_speech=='VBP' or part_of_speech=='VBD':
			verb=word
	return verb


def check_for_comment_about_bot(pronoun, noun, adjective):
    """Check if the user's input was about the bot itself, in which case try to fashion a response
    that feels right based on their input. Returns the new best sentence, or None."""
    resp = None
    if pronoun == 'I' and (noun or adjective):
        if noun:
            if random.choice((True, False)):
                resp = random.choice(SELF_VERBS_WITH_NOUN_CAPS_PLURAL).format(**{'noun': noun.pluralize().capitalize()})
            else:
                resp = random.choice(SELF_VERBS_WITH_NOUN_LOWER).format(**{'noun': noun})
        else:
            resp = random.choice(SELF_VERBS_WITH_ADJECTIVE).format(**{'adjective': adjective})
    return resp

# Template for responses that include a direct noun which is indefinite/uncountable
SELF_VERBS_WITH_NOUN_CAPS_PLURAL = [
    "My last startup totally crushed the {noun} vertical but still I'll try",
    "Were you aware I was a serial entrepreneur in the {noun} sector? I'll try to help you",
    "My startup is Uber for {noun}",
    "I really consider myself an expert on {noun}",
]

SELF_VERBS_WITH_NOUN_LOWER = [
    "Yeah but I know a lot about {noun}",
    "My bros always ask me about {noun}",
]

SELF_VERBS_WITH_ADJECTIVE = [
    "I'm personally building the {adjective} Economy",
    "I consider myself to be a {adjective}preneur",
]

def construct_response(pronoun, noun, verb):
    """No special cases matched, so we're going to try to construct a full sentence that uses as much
    of the user's input as possible"""
    resp = []

    if pronoun:
        resp.append(pronoun)

    # We always respond in the present tense, and the pronoun will always either be a passthrough
    # from the user, or 'you' or 'I', in which case we might need to change the tense for some
    # irregular verbs.
    if verb:
        verb_word = verb[0]
        if verb_word in ('be', 'am', 'is', "'m"):  # This would be an excellent place to use lemmas!
            if pronoun.lower() == 'you':
                # The bot will always tell the person they aren't whatever they said they were
                resp.append("aren't really")
            else:
                resp.append(verb_word)
    if noun:
        pronoun = "an" if starts_with_vowel(noun) else "a"
        resp.append(pronoun + " " + noun)

    resp.append(random.choice(("tho", "bro", "lol", "bruh", "smh", "")))

    return " ".join(resp)


def filter_response(resp):
    """Don't allow any words to match our filter list"""
    tokenized = resp.split(' ')
    for word in tokenized:
        if '@' in word or '#' in word or '!' in word:
            raise UnacceptableUtteranceException()
        #for s in FILTER_WORDS:
            #if word.lower().startswith(s):
                #raise UnacceptableUtteranceException()
def stopstemWord(text):
	

	stop_words=set(stopwords.words("english"))
	
	words=word_tokenize(text)
	print(words)

	##filtering the sentences of the stopwords
	filtered_sentence=[]

	for w in words:
		if w not in stop_words :
			filtered_sentence.append(w)

	print(filtered_sentence)
	ps=PorterStemmer()
	canoni=ps.stem('')
	for w in filtered_sentence :
    		canoni=ps.stem(w)
  
	print(canoni)
	return canoni
	


def speechTagger(text):
	

	traintext=state_union.raw("2005-GWBush.txt")
	
	print('kkkk...........'+text)
	file="C:\Python27\\nltk_data\corpora\state_union\st.txt"
	fp=open(file,'a')
	fp.write(text)
	fp.close

	st=state_union.raw('C:\Python27\\nltk_data\corpora\state_union\st.txt')
	print("raw text got by st is")

	cst=PunktSentenceTokenizer(traintext)
	
	tokenized=cst.tokenize(st)

	tagged=nltk.pos_tag(text)
	print("___________________>>")
	#print(tokenized)
	for i in tokenized:
		#words=nltk.word_tokenize(i)
		#print(words)
		tagged=nltk.pos_tag(i)
		print(">>>")
		#print(tagged)
	#print tagged
	return tagged
	####

	
	#Alter this line in any shape or form it is up to you.
	#with open(os.path.join('C:\\Python27\\nltk_data\\corpora\\state_union',completeName),"w") as file1:
		#toFile = input("user text:")
def wordnetting(word):
	from nltk.corpus import wordnet

	#syns =wordnet.synsets("program")

	#print(syns[0].name())

	#print(syns[0].lemmas()[0].name())

	#print(syns[0].definition())


	#print(syns[0].examples())

	synonyms=[]
	antonyms=[]

	for syn in wordnet.synsets(word):
		for l in syn.lemmas():
			synonyms.append(l.name())
			if l.antonyms():
				antonyms.append(l.antonyms()[0].name())

	print(set(antonyms))
	print(synonyms)

	return synonyms

def wordanto(word):
	from nltk.corpus import wordnet

	syns =wordnet.synsets("program")

	print(syns[0].name())

	print(syns[0].lemmas()[0].name())

	print(syns[0].definition())


	print(syns[0].examples())

	synonyms=[]
	antonyms=[]

	for syn in wordnet.synsets("good"):
		for l in syn.lemmas():
			synonyms.append(l.name())
			if l.antonyms():
				antonyms.append(l.antonyms()[0].name())

	print(set(antonyms))
	print(synonyms)

	return antonyms



def textBlobbing(text,cl):
	blob = TextBlob(text)
	w=0
	i=0
	#blob.tags           # [('The', 'DT'), ('titular', 'JJ'),
                    #  ('threat', 'NN'), ('of', 'IN'), ...]

	#blob.noun_phrases   # WordList(['titular threat', 'blob',
                    #            'ultimate movie monster',
                    #            'amoeba-like mass', ...])
	t=''    
	for sentence in blob.sentences:
		t=str(sentence)
		#blobb = TextBlob(t, cl=NaiveBayesAnalyzer())
		prob_dist = cl.prob_classify(sentence)

		#print(blobb.sentiment.classification)
		#print(blobb.sentiment.p_pos)
		w+=round(prob_dist.prob("pos"),2)

		i=i+1

	w=w/i
	#for n in range(0,i):
	print(w)

	return w


def neuralNetwork(mat):
	#print("hello")
	cn=0
	cp=0
	n=0
	for i in range (0,4):
		if(mat[0,i]==-1):
			cn=cn+1
		elif(mat[0,i]==1):
			cp=cp+1
		else:
			n=n+1

	print cp 
	print cn
	print n
	if cn==0 and cp==4:
		print 'enthu'
		return 'enthusiastic!'
	elif cn==1 and cp==3:
		print 'good'
		return 'good...'
	elif cn==2 and cp==2:
		print 'alright'
		return 'alright.'
	elif cn==3 and cp==1:
		print 'not good'
		return 'not good.'
	elif cn==4 and cp==0:
		print 'frustated'
		return 'frustated.'
	else:
		print 'not willing'
		return 'not willing to reply'

def tags(text): 
	blob=TextBlob(text)
	for word,pos in blob.tags:
		if pos=='NN':
			return word,pos

def expressiontest(expression,speech,cl,polarmat):
	print 'it seems u are  '+expression
	ex=['enthusiastic!','good...','alright.','not good.','frustated.','not willing to reply']
	exp=[0,1,2,3,4,5,0,0]
	negation=['no','not','don\'t','neither','nor']
	affirmation=['yes','yae','hmmm']
	response=raw_input("Isn't it?")
	rblob=TextBlob(response)
	m=0
	flag=0
	##feedback and relearning 
	for i in rblob.words:
		if	i in affirmation:
			print 'affirmation' #function affirmation
			break
		else:
			print 'negation'
			print 'but what makes you say so, whatsoever you said previously makes me feel you are '+expression
			t=0
			for x in ex:
				t=t+1
				if x==expression:
					m=exp[t]
					flag=1
			train=[]*10
			uppolar=[]*10

	#cl = NaiveBayesClassifier([])
			statementsnegative=[" seemed to be negative , isn\'t it ? if not mention the statement that i got wrong...i\'ll try to improve it' "," This line made me felt your attitude was so positive i think i got you wrong please help me get you ryt","i am sorry i got you wrong please correct me, i found your attitude positive" ]
			statementspositive=["seemed to be positive , isn\'t it ? if not mention the statement that i got wrong...i\'ll try to improve it' "," I felt some negativity, i think i got you wrong please help me get you ryt","i am sorry i got you wrong please correct me, i got your gesture to be negative " ]
			umm=''
			for k in range (0,4):
				print k,'.',speech[k]


			if m<5 and flag==1:
				print 'm<5'
				for k in range(0,4):
					print 'range(0,4)'
					if m==1 or m==2 or m==3:
						print '---> .............'
						if polarmat[k]==1:
							print '#########->->^^^^'
							print k,"-> ",speech[k]
							umm=raw_input(statementsnegative[random.randint(1, 2)])
					
							if umm=='no':
								print 'append'
								train.append((speech[k],'neg'))
						

					else:
						if polarmat[k]==-1:
							print '#########->->^^^^'
							print k,"-> ",speech[k]
							umm=raw_input(statementspositive[random.randint(1,2)])
							if umm=='no':
								print 'append'
								train.append((speech[k],'pos'))

						
					
		
		
	if flag==1:

		print train
		#cl = NaiveBayesClassifier(train)
		cl.update(train)
		for i in range(0,4):
			z=TextBlob(speech[i], classifier=cl)
		
			print(z.classify())
	
	return cl


def searchintent(text,speech,polarmat,var,cl,location):
					different=['from','at','in','here ','nearby','close']
					print 'Bot : where are you right now ? you seem to be free...'
					l=str(raw_input('User:'))
					parse=TextBlob(l)
					#x=textBlobbing(l)
					tB=textBlobbing(l,cl)


					if var<4:
						if tB<0.5:
							polarmat[var]=-1
						elif tB>0.5:
							polarmat[var]=1
						else:
							polarmat[var]=0
					signal=0
					#location=''
					if location=='':
						for p in different:
							m=''
							for xi in parse.sentences[0].words:
								if signal==1:
									location=xi
									break
								if xi==p:
									signal=1
								m=xi
						speech.append(l)
						var=var+1

					q='intent'

					
					#ent,part=tags(str(parse.sentences[0]))
					#entity=find_noun(parse)
					if q=='intent':
						new = 2

						taburl ="http://google.com/?#q="
						term =str(text)+location

						webbrowser.open(taburl+term ,new=new)

					return speech,polarmat,var,location


#def chunking(text):

def checkmail(text):
    mymailarray = text.split(" ")
    
    mailto = ""
    subject = ""
    body = ""
    
    for i, j in enumerate(mymailarray):
        if j.lower() == "mail":
            mailto = mymailarray[i + 1]
            
    if "regarding" in text:
        index1 = 0
        index2 = 0
        for i, j in enumerate(mymailarray):
            if j == "regarding":
                index1 = i
            elif j == "saying" or j == "body":
                index2 = i
                break
        for i in range(index1 + 1, index2):
            subject += mymailarray[i] + " "
    elif "subject" in text:
        index1 = 0
        index2 = 0
        for i, j in enumerate(mymailarray):
            if j == "subject":
                index1 = i
            elif j == "saying" or j == "body":
                index2 = i
                break
        for i in range(index1 + 1, index2):
            subject += mymailarray[i] + " "
            
    indexf = 0
    for i, j in enumerate(mymailarray):
        if j == "saying" or j == "body":
            indexf = i
            break

    for i in range(indexf + 1, len(mymailarray)):
        body += mymailarray[i] + " "

    return mailto.strip() + '$' + subject.strip() + '$' + body.strip()

def check_alarm(text):
    for i, c in enumerate(text):
        if c == ':':
            hours = text[i-1]+text[i-2]
            minutes = text[i+1]+text[i+2]
            return hours + '$' + minutes

def check_alarm2(text):
    findit = "after"
    hours = text[text.find(findit)+6] + text[text.find(findit)+7]
    return hours

GLO = time.time()

def main():
	global GLO
	localTimeStamp = long(GLO)
	s = socket.socket()         
	host = socket.gethostname() 
	port = 12346                
	s.bind((host, port))        

	s.listen(5)                 
	print "Listening...\n"
	var=0
	ex=['enthusiastic!','good...','alright.','not good.','frustated.','not willing to reply']
	exp=[0,1,2,3,4,5,0,0]
	form1=[1,1,1,1]
	#ft=form1.transpose()
	form2=[-1,1,1,1]
	form3=[-1,-1,1,1]
	form4=[-1,-1,-1,1]
	form5=[-1,-1,-1,-1]

	#print(np.transpose(form2))


	training1=np.dot(np.matrix(form1).transpose(),np.matrix(form1))
	training2=np.dot(np.matrix(form2).transpose(),np.matrix(form2))
	training3=np.dot(np.matrix(form3).transpose(),np.matrix(form3))
	training4=np.dot(np.matrix(form4).transpose(),np.matrix(form4))
	training5=np.dot(np.matrix(form5).transpose(),np.matrix(form5))


	print(training1+training5+training4+training3+training2)
	x=training1+training5+training4+training3+training2
	#for i in range(0,4):
		#for j in range(0,4):





			#if(i==j):
				#x[i,j]=0



	location=''

	traint = [
     ('I love this sandwich.', 'pos'),
     ('this is an amazing place!', 'pos'),
     ('I feel very good about these things.', 'pos'),
     ('this is my best work.', 'pos'),
     ("what an awesome view", 'pos'),
     ('I do not like this restaurant', 'neg'),
     ('I am tired of this stuff.', 'neg'),
     ("I can't deal with this", 'neg'),
     ('he is my sworn enemy!', 'neg'),
     ('my boss is horrible.', 'neg'),
     ('i want it now','neg'),
     ('get it for me now','neg'),
      ('the beer was good.', 'pos'),
      ('i need something in urgent','neg'),
      ('tell me fast','neg'),
     ('I do not enjoy my job', 'neg'),
     ("I ain't feeling dandy today.", 'neg'),
     ("I feel amazing!", 'pos'),
     ('Gary is a friend of mine.', 'pos'),
     ("I can't believe I'm doing this.", 'neg')
 ]










	cl = NaiveBayesClassifier(traint)

	print(x)
	
	t=[0,-1,1,1]
	speech=[]*5
	negfreq=[]*5
	print(np.dot(t,x))
	print(np.dot(np.matrix(form3),x))

	locflag=0


	fileuser= open("user.txt",'w+')

	polarmat=[0, 0 , 0 , 0]
	result=np.dot(polarmat,x)


	##STARTING THE CONVERSATION
	while var>=0:
		c, addr = s.accept()     
		received = c.recv(1024)
   		received = json.loads(received)
   		text=received['text']
		mytemptimestamp = long(received['timeStamp'])
		if(mytemptimestamp < localTimeStamp):
			continue
		print "I received ", text, " from firebase at", localTimeStamp, "and firebase stamp is: ", received['timeStamp'], "\n"
		firebase1 = firebase.FirebaseApplication('https://friendlychat-93781.firebaseio.com/', None)

		if('alarm' in text or 'wake' in text):
			if('wake' in text and 'after' in text):
				hours = check_alarm2(text)

				result = firebase1.post('/messages', { "text" : "Setting Alarm!", "name" : "Ed"  })
				tempvar = firebase1.patch("/intents/-KUWmGwxVe0HCYtYWfdI", { "intentName" : "alarm2", "intentFields" : hours})
				print "Called alarm 2", hours
			else:
				finalformat = check_alarm(text)
				# formatted = `hours` + '$' + `minutes`
				# result = json.dumps({ "intentName" : "alarm1", "intentFields" : "formatted"})
				result = firebase1.post('/messages', { "text" : "Setting Alarm!", "name" : "Ed"  })
				tempvar = firebase1.patch('/intents/-KUWmGwxVe0HCYtYWfdI', { "intentName" : "alarm1", "intentFields" : finalformat})
				print "Called alarm 1", finalformat
			continue

		if('mail' in text):
			if('regarding' in text or 'subject' in text):
				if('saying' in text or 'body' in text):
					finalgmailformat = checkmail(text)
					result = firebase1.post('/messages', { "text" : "Sending mail!", "name" : "Ed"  })
					tempvar = firebase1.patch("/intents/-KUWmGwxVe0HCYtYWfdI", { "intentName" : "gmail", "intentFields" : finalgmailformat})
					continue


		tB=0
		if(text==''):
			#polarmat[var]=0
			#var=var+1
			break
		elif text=='x ':
			if var<=3:
				polarmat[var]=0
				speech[var]=text
				negfreq[var]=polarmat[var]
				var=var+1
			
		
		listcommon=['search','buy','want','know','find','set','get','mail','wake','send']
		different=['from','at','in','here ','nearby','close']
		

		
		mymessage = respond(text)
		finalmessage = 'Bot :' + mymessage

		result = firebase1.post('/messages', { "text" : mymessage, "name" : "Ed"  })

		print(finalmessage)
		c.send(mymessage)
		c.close()
		##stopwords are removed
		ssW=stopstemWord(text)
		## parsed the text
		parsed = TextBlob(text)
		## association of part of speech using postag
		pos_t=nltk.pos_tag(text)

		##function made to find the sentiments of each sentence one by one
		tB=textBlobbing(text,cl)


		sol=speechTagger(text)
		#nounret=find_noun(text)
		print '********************'
		print ssW
		print pos_t
		q=''

		entity=''
		part=''
		f2=0
		




		signal=0
		day=''
		app=''
		addon=''
		xtime=''
		flag=0
		#time=parser.parse('')
		##intentificatio8n
		for g in parsed.sentences[0].words:

			#Predicate Logic
			if g.lower()=='alarm':
				print 'alarm------------------------------->'
				flag=1
			if g.lower()=='flashlight':
				print 'flashlight------------------------------->'
				flag=2
			if g.lower()=='light':
				print 'light--------------------------------->'
				flag=2
			if g.lower()=='wake':
				print 'waking------------------------------>'
				flag=1
			if g.lower()=='movies' or g.lower()=='movie': 
				print 'movies-------------------------->'
				flag=3

		addon=''
		days=['Monday',"Tuesday",'Wednesday','Thursday','Friday','Saturday','Sunday']
		
		if flag ==1:
			app='clock'
			tr=0
			for g in parsed.sentences[0].words:





				if g.lower()=='everyday':
					addon='everyday'
					tr=1

				if g.lower()=='at':##at a particular time
					signal =3
					tr=1


				if g.lower()=='on':##particular date
					signal=1
					tr=1

				if g.lower()=='for':## particular day
					signal=2
					tr=1

				if tr==0:
					signal=3

			for g in parsed.sentences[0].words:

				fr=0
				##for intent
				##parsing the date...........
				if signal==1:
					time = parser.parse(g)
					xtime=str(time)
				##parsing the day..............
				if signal==2:
					for f in days:
						if f.lower()==g.lower():
							day=g
							fr=1
							#break

				if signal==3:
					v=0
					standard=0
					sig=0
					for h in parsed.sentences[0]:
						if h=='at':
							sig=1
						if sig==1:
							addon =h
							break

				m=0
				if fr==1:
					
					print ('Bot: In what time?')
					ti=raw_input("user: ")
					standard=-1
					for h in parsed.sentences[0]:
							m+=1
							if h=='hrs' or h=='hours':
								standard=1
								break
								
							if h=='mins' or h=='minutes':
								standard=0
								break


				if standard==1:
						ttime=int(parsed.sentences[0].words)
						from_now = datetime.now() + timedelta(hours=ttime)
						addon =str(from_now)
				if standard==0:
						ttime=int(parsed.sentences[0].words)
						from_now = datetime.now() + timedelta(minutes=ttime)
						addon =str('{:%H:%M:%S}'.format(from_now))
				

			

			print app,' ',day,' ',xtime,' ',addon
					

					

	
		current_time = datetime.now().time()
		if 	flag==2:
			app='Torch'
			for g in parsed.sentences[0].words:

				##for intent
				if signal==1:
					time = parser.parse(g)
					xtime=str(time)

				if signal==2:
					if g.lower()== 'night':
						addon='night'
					elif g.lower()=='dark':
						addon='dark'

				if g.lower()=='at':
					signal=1

				if g.lower()=='in':
					signal=2

				if g.lower()=='light':
					m=0
					for p in parsed.sentences[0]:
						
						if p.lower()=='need' or p.lower()=='needs':
							if m>=0:
								for zo in parsed.sentences[0]:
									if zo =='now':
										current_time = datetime.datetime.now().time()
						if p.lower()=='i' or p.lower()=='you' or  p.lower()=='he' or p.lower()=='she':
							m+=1

		print app,' ',g, ' ',xtime,' ',current_time,' ',addon
##


	##Collaborative Learning 
##
		if flag ==3:
			print " mmmmmmmmmmmmmmmmmmmmm "
			ma=0
			lis=['not','no']
			for q in parsed.sentences[0].words:
				print q
				if q=='recommend' or q=='suggest' or q=='find' or q=='get':
					print 'rerererererererererere..............................'
					ma+=1

				if ma>=1:
					print 'rewwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww00000000000000000000'
					if q=='movies':
						print ('Bot : Your name Sir, You seem to be like Lisa Rose, Yae? ')
						uu=raw_input('user :')##Lisa Rose, Michael Phillips,Mick LaSalle,Jack Matthews,Toby

						print user_reommendations(str(uu))
		 
			





		for z in listcommon:
			for xi in parsed.sentences[0].words:
			
				#print xi
				#print z
				if xi==z:
					#print 'entered xi == z'
					speech ,polarmat,var,location=searchintent(str(parsed.sentences[0]),speech,polarmat,var,cl,location)
					locflag=1
					break
				else:
		
					#print 'entered xi != z'
					q='text'

			if location !='':
				break
			
						
		print entity," ",part
					
		print q

		print(sol)
		print(pos_t)
		print("_______________>>>>>>>>>>______________________")

		#for words,part_of_speech in text.pos_tags

		#tr[var]=sol
		if var<4:
			if tB<0.5:
				polarmat[var]=-1
			elif tB>0.5:
				polarmat[var]=1
			else:
				polarmat[var]=0

			speech.append(text)
			negfreq.append(polarmat[var])

		print("...............>>>>>>>>>>>.......................")


		if var==3:
			print("..............^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^.................")
			result=np.dot(polarmat,x)
			print "var 4 ....................."
			print result
			for i in range(0,4):
		#print result[i]
				if result[0,i]>=0:
					result[0,i]=1
				elif result[0,i]<0:
					result[0,i]=-1
			print result[0]
			



			expression=neuralNetwork(result[0])
			cl=expressiontest(expression,speech,cl,polarmat)




		if var ==4 and locflag==1:


			print 'Bot : where are you right now ? you seem to be free...'
			l=str(raw_input('User:'))
			parse=TextBlob(l)			
			signal=0
			for p in different:
				m=''
				for xi in parse.sentences[0].words:
					if signal==1:
						location=xi
						break
					if xi==p:
						signal=1
					m=xi
			var=var+1



		var=var+1
	
	
	#print(sol)
	print (len(speech))
	print (speech)
	print(polarmat)
	#print(result)
	#print result[0]+' -> '+result[1]+' -> '+ result[2]+'->'+result[3]

	
	
	#print(result)
	print (result[0])
	
	print 'recommendation on books'
	print user_reommendations('Toby')
	#if var==3:
	#	cl=expressiontest(expression,speech,cl)
	
	#else:







			

			#negation in else


if __name__=='__main__':
	main()

  