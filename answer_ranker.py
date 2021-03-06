from time import sleep
import re
import nltk
class BasicAnswerRanker(object):
    def __init__(self, documents, qas):
        self.classifier = BasicQueryClassifier(documents, qas)
        self.rank_no = 1
        self.pos_cache = {}

    def rank_list(self, entity_list, query):
        first_pass_result = self.first_pass(entity_list, query)
        second_pass_result = self.second_pass(first_pass_result, query)
        third_pass_result = self.third_pass(second_pass_result, query)
        return third_pass_result

    def first_pass(self, entity_list, query):
        high_ranked = []
        low_ranked = []
        for entry in entity_list:
            if content_words_appear_in_query(entry, query):
                low_ranked.append(entry)
            else:
                high_ranked.append(entry)
        return [high_ranked, low_ranked]

    def second_pass(self, first_pass_result, query):
        tag = self.classify(query)
        result = []
        for l in first_pass_result:
            high_ranked = []
            low_ranked = []
            for entry in l:
                for entity in entry[1]:
                    if entity[0] == tag:
                        high_ranked.append((entry[0], entity[1]))
                    else:
                        low_ranked.append((entry[0], entity[1]))
            result.append(high_ranked)
            result.append(low_ranked)
        return result


    def third_pass(self, second_pass_result, query):
        result = []
        for l in second_pass_result:
            ra = []
            for entry in l:
                rank = self.get_rank(entry, query)
                ra.append((rank, entry[1]))
            ra = sorted(ra, key=lambda x: x[0])
            ra = map(lambda x: x[1], ra)
            result.extend(ra)
        return result

    def classify(self, query):
        return self.classifier.classify(query)

    def get_rank(self, entry, query):
        CLOSED_CLASS_TAGS = [ #  pronouns, determiners, conjunctions, modals and prepositions.
            'CC',   #  Coordinating conjunction
            'DT',   #  Determiner
            'IN',   #  Preposition or subordinating conjunction
            'MD',   #  Modal
            'PRP',  #  Personal pronoun
            'PRP$', #  Possessive pronoun
            'WDT',  #  Wh-determiner
            'WP',   #  Wh-pronoun
            'WP$'   #  Possessive wh-pronoun
            ]
        try:
            closed_words = self.pos_cache[query]
        except KeyError:
            text = self.break_query(query.lower())
            try:
                tagged = nltk.pos_tag(text)
            except LookupError:
                nltk.download('averaged_perceptron_tagger')
                tagged = nltk.pos_tag(text)
            closed = []
            for tup in tagged:
                tag = tup[1]
                word = tup[0]
                if tag in CLOSED_CLASS_TAGS:
                    closed.append(word)
            self.pos_cache[query] = closed
            closed_words = closed
        rank = 1000
        if len(closed_words) > 0:
            tags_to_check = self.check_tags(entry[0], closed_words)
            if len(tags_to_check) > 0:
                text = ' '.join(self.break_query(entry[0].lower()))
                text = text.split(entry[1].lower())
                assert(len(text) > 1)
                for i in range(len(text) - 1):
                    lower = text[i].split()
                    low_val = -1
                    upper = text[i + 1].split()
                    up_val = -1
                    for i in range(len(lower)):
                        if lower[-1 - i] in tags_to_check:
                            low_val = i + 1
                    for i in range(len(upper)):
                        if upper[i] in tags_to_check:
                            up_val = i + 1
                    if low_val > 0 and low_val < rank:
                        rank = low_val
                    if up_val > 0 and up_val < rank:
                        rank = up_val
        return rank

    def check_tags(self, sentence, closed_words):
        lsentence = sentence.lower()
        result = []
        for word in closed_words:
            if word in lsentence:
                result.append(word)
        return result

    def break_query(self, query):
        parsed_query = re.sub('[,.[\]();:?!]', ' ', query)
        parsed_query = re.sub('[^a-zA-Z0-9 ]', '', parsed_query)
        return parsed_query.split()
def content_words_appear_in_query(entry, query):
    content_words = map(lambda x: x[1], entry[1])
    for word in content_words:
        if word not in query:
            return False
    return True

class BasicQueryClassifier:
    def __init__(self, documents, qas):
        # Tags are: PERSON, LOCATION, NUMBER, OTHER
        self.documents = documents
        self.qas = qas
        self.yes = 0
        self.no = 0
        self.rules = [
            ('person','PERSON'),
            ('location', 'LOCATION'),
            ('number','NUMBER'),
            ('who', 'PERSON'),
            ('why', 'OTHER'),
            ('are', 'OTHER'),
            ('from', 'LOCATION'),
            ('country', 'LOCATION'),
            ('where', 'LOCATION'),
            ('when', 'NUMBER'),
            ('many', 'NUMBER'),
            ('year', 'NUMBER'),
            ('decade', 'NUMBER'),
            ('time', 'NUMBER'),
            ('cost', 'NUMBER'),
            ('population', 'NUMBER')
        ]
    def classify(self, query):
        for rule in self.rules:
            word = rule[0]
            tag = rule[1]
            if word in query.lower():
                return tag
        return 'UNKNOWN'
        