from django.db import models
import json
import sys
import csv
import pandas as pd
import numpy as np

#adding the directory where I have the words for the main model.
sys.path.append('/home/gilberto/workspace/projectos/myself/mySelfApp/words/')

class counter(models.Model):
    name = models.CharField(max_length=100)
    count = models.IntegerField(default=0)

#Classes
class Sentence(models.Model):
    text = models.CharField(max_length=200)
    target = models.CharField(max_length=100, default='')
    verbs = models.CharField(max_length=150, default='')
    booleans = models.CharField(max_length=100, default='') #1: positive, 2:negative, 0:none
    emotions = models.CharField(max_length=150, default='')
    sign = models.CharField(max_length=10, default='') #true, false
    action = models.IntegerField(default=0)
    unaction = models.IntegerField(default=0)
    text = text

    def __str__(self):
        return '\ntext: {}\ndb: {}\nverbs: {},\nemotions: {}\nsign: {}, booleans: {}\n'.format(self.text, self.target, self.verbs, self.emotions, self.sign, self.booleans)

    #STATS 
    def get_stats_data(self):
        data:dict = {
            'Activities': Sentence.objects.filter(target='user_emotion_actions'),
            'Objects': Sentence.objects.filter(target='user_emotion_objects'),
            'Contexts': Sentence.objects.filter(target='user_emotion_context'),
            'Bridges': Sentence.objects.filter(target='user_emotion_bridge'),
        }
        return data 

    #INSERT SITUATION
    def user_response(self, text:str):
        isList = True
        ans = ''
        #getting list word
        if 'list' not in text:
            isList = False
        #getting emotions

        if isList:
            response, message = self.list_response(text)
        #Emotion bridge answer
        else:
            response, message = self.emotional_bridge_response(text)
        return response, message

    def emotional_bridge_response(self, text:str):
        message = 'This is a memory of how you faced a similar situation: '
        emotions = self.get_words_from_category(self.remove_signs(text), 'emotions')
        db_sentences = Sentence.objects.filter(target="user_emotion_bridge")
        sentences = {}

        #filter all the sentences that includes the ones that has the emotion that I mentioned
        for emotion in emotions:
            sentences[emotion] = []
            for sentence in db_sentences:
                s_emotions = json.loads(sentence.emotions)
                if emotion in s_emotions[0]:
                    sentences[emotion].append(sentence)

        #get the best result from all
        response = {'text': '', 'repeated_words': 0, 'id': None}
        for key, value in sentences.items():
            for el in value:
                counter = self.count_repeated_words(el.text, text)
                if(counter > response['repeated_words']):
                    response = {'text': el.text, 'repeated_words': counter, 'id': el.id}

        #restruct the response
        print(response)
        return  response, message

    def get_movement_percentage(self):
        positive, negative = self.get_total_movements()
        total = positive + negative
        if(total == 0): return 0
        percentage = (positive * 100) / total
        return percentage
    
    def list_response(self, text:str):
        print('GetAnswerQuerty()')
        text =  " ".join(" ".join(text.split('.')).split(','))
        sentences = []
        selected_sentence = {'text': '', 'words': 0}
        verbs = self.get_words_from_category(sentence=text, category='verbs')
        message = 'This is a list of things you like to {}'.format(", ".join(verbs))
        print(text)
        if len(verbs) > 0:
            for i in range(len(verbs)):
                if 'things' in text and verbs[i] in text:
                    print('#actions section#')
                    db_sentences = Sentence.objects.filter(target='user_emotion_actions')
                    print(db_sentences)
                    boolean = self.get_words_from_category(text, 'negative_booleans') or True
                    emotions = self.get_words_from_category(text, 'emotions') 
                    print(boolean)
                    print(emotions)
                    print(verbs[i])
                    #filter by booleans and emotions
                    for s in db_sentences:
                        for j in range(len(emotions)):
                            print(j)
                            print(json.loads(s.booleans))
                            print(json.loads(s.emotions)[0][0])
                            print(json.loads(s.verbs)[0][0])
                            if json.loads(s.booleans)[0] == boolean and json.loads(s.emotions)[0][0] == emotions[j] and json.loads(s.verbs)[i][0] == verbs[i]:
                                sentences.append(s)
                    return sentences, message

        if 'things' in text:
            #e.x.sentence: list of things I like
            print('#things section#')
            db_sentences = Sentence.objects.filter(target='user_emotion_object')
            boolean = self.get_words_from_category(text, 'negative_booleans') or True
            emotions = self.get_words_from_category(text, 'emotions') 
            sentences = []

            for s in db_sentences:
                for j in range(len(emotions)):
                    print(j)
                    print(json.loads(s.booleans))
                    print(json.loads(s.emotions)[0][0])
                    if json.loads(s.booleans)[0] == boolean and json.loads(s.emotions)[0][0] == emotions[j]:
                        sentences.append(s)
            return sentences, message

        else:
            print('#context section#')
            db_sentences = Sentence.objects.filter(target='user_emotion_context')
            boolean = self.get_words_from_category(text, 'negative_booleans') or True
            emotions = self.get_words_from_category(text, 'emotions') 
            sentences = []

            for s in db_sentences:
                for j in range(len(emotions)):
                    print(j)
                    print(json.loads(s.booleans))
                    print(json.loads(s.emotions))
                    print(json.loads(s.emotions)[0][0])
                    if json.loads(s.booleans)[0] == boolean and json.loads(s.emotions)[0][0] == emotions[j]:
                        sentences.append(s)
            return sentences, message




    #INSERT OBSERVATION (DONE)
    def analyzeSentence(self):
        # print('\nanalyseSentence():')
        sentences_data:dict = self.get_sentences_data()
        #do nothing if there is no sentences
        if(sentences_data == {}): return True
        #TODO: Insertar el apartado "insertSentenceToDB()" 
        self.insertSentenceToDB(sentences_data)

    @classmethod
    def insertSentenceToDB(cls, sentences_data:dict):
        for i in range(len(sentences_data['sentences'])):
            s = cls(text=sentences_data['sentences'][i],
                    emotions=json.dumps(sentences_data['emotions'][i]),
                    verbs=json.dumps(sentences_data['verbs'][i]),
                    booleans=json.dumps(sentences_data['booleans'][i]),
                    sign=json.dumps(sentences_data['signs'][i]),
                    target=sentences_data['target'][i],
                    )
            s.save()

    def get_sentences_data(self):
        sentences = self.select_emotional_sentences()
        #do nothing if there is no sentences
        if(len(sentences) < 1): return dict({})
        sentences_data = {
            'sentences': sentences,
            'emotions': [],
            'signs': [],
            'booleans': [],
            'target': [],
            'verbs': [],
        }
        i = 0
        while i < len(sentences):
            sub_sentences = sentences[i].split(',') 
            #filling some extra information
            sentences_data['emotions'].append(self.get_divided_words_from_categories(sentences[i], 'emotions')) #TODO: Hacer una funcion similar a get_booleans() para las emociones y los verbos (done!)
            sentences_data['booleans'].append(self.get_booleans(sentences[i]))
            sentences_data['verbs'].append(self.get_divided_words_from_categories(sentences[i], 'verbs'))

            #potencialy compund sentences
            if len(sub_sentences) > 1:
                sub_sentence_categories = self.get_words_categories(sub_sentences[0])
                next_sub_sentence_categories = self.get_words_categories(sub_sentences[1])
                #case 1: emotional bridge
                if 'emotions' in sub_sentence_categories and 'emotions' in next_sub_sentence_categories:
                    if self.is_positive(self.get_words_from_category(sub_sentences[i], 'emotions')) == False and self.is_positive(self.get_words_from_category(sub_sentences[i+1], 'emotions')):
                        sentences_data['target'].append('user_emotion_bridge')
                        sentences_data['signs'].append([False, True])
                        i += 1
                        continue
            #case 2: emotional with action sentence
            sub_sentence_categories = self.get_words_categories(sub_sentences[0])
            if 'verbs' in sub_sentence_categories:
                sentences_data['target'].append('user_emotion_actions')
                sub_sentence = " ".join(" ".join(sub_sentences).split(',')) #get an string without . and , 
                sentences_data['signs'].append(self.is_positive(sub_sentence))
                i += 1
                continue
            #case 3: emotional with objects
            elif 'object' in sub_sentence_categories and 'verbs' not in sub_sentence_categories:
                sentences_data['target'].append('user_emotion_object')
                sub_sentence = " ".join(" ".join(sub_sentences).split(',')) #get an string without . and , 
                sentences_data['signs'].append(self.is_positive(sub_sentence))
                i += 1
                continue
            #case 4: emotional with context
            elif 'prepositions' in sub_sentence_categories and 'verbs' not in sub_sentence_categories:
                sentences_data['target'].append('user_emotion_context')
                sub_sentence = " ".join(" ".join(sub_sentences).split(',')) #get an string without . and , 
                sentences_data['signs'].append(self.is_positive(sub_sentence))
                i += 1
                continue
            i += 1
        print('\nget_sentences_data(): ')
        print(sentences_data)
        return sentences_data

    def select_emotional_sentences(self):
        sentences = str(self.text).split('.') 
        sub_sentences_list:list = []
        print('\nSelect_emotional_sentences()')
        print('sentences: ')
        print(sentences)
        i = 0
        j = 0

        #going through each sentence divided by . (dot)
        while i < len(sentences):
            sub_sentences = sentences[i].split(',')
            print('\nsub sentences: ')
            print(sub_sentences)
            #going through each sentence divided by , (coma)
            while j < len(sub_sentences):
                #This condition saves me from index error.
                if j < len(sub_sentences) - 1:
                    sub_sentence_categories = self.get_words_categories(sub_sentences[j])
                    next_sub_sentence_categories = self.get_words_categories(sub_sentences[j + 1])
                    #in case of a emotional bridge
                    if('emotions' in sub_sentence_categories and len(sub_sentence_categories) >= 4 and 'emotions' in next_sub_sentence_categories and len(next_sub_sentence_categories) >= 4):
                        if not self.is_positive(self.get_words_from_category(sub_sentences[i], 'emotions')) and self.is_positive(self.get_words_from_category(sub_sentences[i + 1], 'emotions')):
                            sub_sentences_list.append(", ".join([sub_sentences[i], sub_sentences[i + 1]]))
                            j += 2
                            continue
                    #add a sentence that has everything to be added
                    elif('emotions' in sub_sentence_categories and len(sub_sentence_categories) >= 4):
                        sub_sentences_list.append(sub_sentences[i])
                        continue
                    #add a sentence that contains two sub-sentences because one sub-sentence does not have emotions
                    elif('emotions' not in sub_sentence_categories and 'emotions' in self.get_words_categories(sub_sentences[j + 1])):
                        j += 1
                        sub_sentences_list.append(sub_sentences[i][0] + ', ' + sub_sentences[i + 1][0])
                        continue
                    #ommit if the sentence of index j and j+1 have no emotion
                    elif('emotions' not in sub_sentence_categories and 'emotions' not in self.get_words_categories(sub_sentences[j + 1])):
                        continue 
                #there is no posibilities of having any emotional bridge here.
                else:
                    #add a sentence that has everything to be added
                    sub_sentence_categories = self.get_words_categories(sub_sentences[j])
                    print(sub_sentence_categories)
                    if('emotions' in sub_sentence_categories and len(sub_sentence_categories) >= 4):
                        sub_sentences_list.append(sub_sentences[i])
                        j += 1
                        continue
                j += 1
            i += 1
        
        print('\nSentences selected: ')
        print(sub_sentences_list)
        return sub_sentences_list




    #handlers
    def is_list(self, sentence:str):
        pass

    def is_positive(self, emotions:list):
        """
        This method calculates if a sentences has more or less positive emotions
        Input: 
            emotions (list)
        Output:
            True/False
        """
        emotions_db = pd.read_csv(sys.path[-1]+'emotions.csv')
        emotions_list:list = []
        #getting the sign of the emotions
        print('\nis_positive()')
        print(emotions)
        for e in emotions:
            for key, val in emotions_db.iterrows():
                if e == val.word:
                    emotions_list.append(val.sign)

        print(emotions_list)
        #calculating the percentage of positive emotions (if positive > 60% is positive)

        if(sum(emotions_list) == 0): return False

        percentage = (sum(emotions_list) / len(emotions_list)) * 100 
        if percentage >= 60:
            return True
        return False

    def get_divided_words_from_categories(self, sentence:str, category:str):
        """
        This method takes the sentence with the first filter by dot. 
        Input:
            sentence(str)
        Output:
            words(list): [['like', 'enjoy'], ['kick', 'play']]
        """
        sentence = sentence.split(',')
        category_words = np.array(pd.read_csv(sys.path[-1]+'{}.csv'.format(category)).loc[:, ['word']])
        print(category_words)
        print(sentence)
        words = []
        for i in range(len(sentence)):
            element = []
            for word in sentence[i].split():
                if word in category_words:
                    element.append(word)
            words.append(element)

        print('\nget_divided_words_from_categories(), cat: {}'.format(category))
        print(words)
        return words
    
    def get_booleans(self, sentence:str):
        sentence = sentence.split(',')
        category_words = np.array(pd.read_csv(sys.path[-1]+'negative_booleans.csv'))
        booleans_list:list = []
        for i in range(len(sentence)):
            sub_boolean = True
            for word in sentence[i]:
                if word in category_words:
                    print(word, category_words)
                    sub_boolean = False
                    break
            booleans_list.append(sub_boolean)

        print('\nget_booleans():')
        print(booleans_list)
        return booleans_list

    def get_words_from_category(self, sentence:str, category:str):
        """
        This method takes a string and returns the words that fits in a specific category
            Input:
                sentence(string)
                category(string)
            Output:
                words_list(list)
        """
        sentence = sentence.split(',')
        category_words = pd.read_csv(sys.path[-1]+'{}.csv'.format(category))
        words_list = []
        print(category_words)
        print(sentence)
        for i in range(len(sentence)):
            for word in sentence[i].split():
                for key, val in category_words.iterrows():
                    if word == val['word']:
                        words_list.append(word)
        print(words_list)
        return list(set(words_list))

    def get_words_categories(self, sentence:str):
        """
        This method aims to sub sentences, those that are closer to be used.
        return:
            cat_list:list [1 x N] :list of emotions (emotions can be repeated)
        """
        categories = {
            'subjects': np.array(pd.read_csv(sys.path[-1]+'subjects.csv')),
            'verbs': np.array(pd.read_csv(sys.path[-1]+'verbs.csv')), 
            'emotions': np.array(pd.read_csv(sys.path[-1]+'emotions.csv')),
            'negatvie_booleans': np.array(pd.read_csv(sys.path[-1]+'negative_booleans.csv')), 
        }
        #getting sub, verbs, emotions, and booleans.
        cat_list:list = []
        sentence = sentence.split(' ')
        for word in sentence:
            for cat in categories:
                if word.lower() in categories[cat]:
                    cat_list.append(cat)
        #getting prepositions or object
        if len(sentence) - len(cat_list) == 1:
            cat_list.append('object')
        elif len(sentence) - len(cat_list) > 1:
            cat_list.append('prepositions')
        #setting positive boolean in case of none negative boolean
        if 'negative_booleans' not in cat_list:
            cat_list.append('positive_booleans')
        #setting an subject in case of having emotions
        if 'emotions' in cat_list and 'subjects' not in cat_list:
            cat_list.append('subjects')

        return cat_list


    def joinListIntoStrList(self, elements:list):
        string = ''
        for i in range(len(elements)):
            if i == len(elements) - 1:
                string += elements
                break
            string += elements + ','

    def remove_signs(self, sentence):
        return " ".join(" ".join(sentence.split('.')).split(','))

    def get_unique_list(self, elements):
        return list(set(elements))

    def count_repeated_words(self, text1:str, text2:str):
        print('Count_repeated_words():')
        print(text1)
        print(text2)
        text1 = self.get_unique_list(self.remove_signs(text1).split())
        text2 = self.get_unique_list(self.remove_signs(text2).split())
        counter = 0
        for el in text2:
            if el in text1:
                counter += 1
        print(counter)
        return counter

    def get_total_movements(self):
        print('get_total_movements()')
        positive = 0
        negative = 0
        sentences = Sentence.objects.all()
        for el in sentences:
            positive += el.action
            negative += el.unaction
        print(el.action)
        print(el.unaction)
        
        return positive, negative

