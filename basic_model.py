from entity_tagger import BasicEntityTagger
from answer_ranker import BasicAnswerRanker
import re
class BasicModel:

    def __init__(self, documents, qas):
        print 'Building Model ... ',
        self.documents = documents
        print 'Initialising Sentence Tagger ... ',
        self.tagger = BasicEntityTagger(documents)
        print 'Initialising Answer Ranker ... ',
        self.ranker = BasicAnswerRanker(documents, qas)
        print 'Done!'

    def sentence_retrival(self, query, documents):
        # documents will be a list each element of that list will in turn be a list of sentences from a wikipedia article
        # query will be a string
        # function should return a single sentence for each wikipedia article
        sentences = []
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
        #                              #
        # The following is test code!! #
        #                              #
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
        for document in self.documents:
            sentences.append(document[0])
        # TODO code this
        assert(len(documents) == len(sentences))
        return sentences


    def entity_extraction(self, sentences):
        # sentences will be a list of sentences each from a unique wikipedia article
        # function should return a list of tuples the first element of the tuple is the input sentence and the second
        # element is a list of entities in that sentence

        entity_list = []
        for sentence in sentences:
            entities = self.tagger.tag(sentence)
            entity_list.append((sentence, entities))

        assert(len(sentences) == len(entity_list))
        return entity_list

    def answer_ranking(self, query, entity_list):
        # query will be a string
        # entity list is a list of tuples the first element of the tuple is the input sentence and the second
        # element is a list of entities in that sentence
        # these entities are tuples where the first element is the tag and the second is the object
        # e.g. (u'LOCATION', u'United States')
        # function should return a list of answers in order of their ranking

        ranked_answers = self.ranker.rank_list(entity_list, query)

        return ranked_answers

    def select_answer(self, ranked_answers):
        # ranked_answers is a list of answers in order of their ranking
        # function should return the selected answer
        answer = ''
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
        #                              #
        # The following is test code!! #
        #                              #
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
        answer = ranked_answers[0]
        # TODO code this
        return answer

    def answer_query(self, query):
        sentences = self.sentence_retrival(query, self.documents)
        entity_list = self.entity_extraction(sentences)
        ranked_answers = self.answer_ranking(query, entity_list)
        return self.select_answer(ranked_answers)

