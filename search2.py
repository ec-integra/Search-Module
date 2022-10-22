from nltk.stem.snowball import SnowballStemmer 
import pymorphy2
import re

def preproccess_delete_affix(word):
    """
    Функция для грубого удаления приставки (не по правилам словообразования). 

        :param word - слово для удаления приставки
            :type str
        
        :param:out ord - слово после удаления приставки
            :type str
    """
    affixArray = {
            'в': ['внутри', 'возо', 'вне', 'воз', 'вос', 'взо', 'вз', 'во', 'вы', 'вс', 'во'],
            'п': ['противо', 'после', 'преди', 'предо', 'пере', 'пред', 'подо', 'поза', 'подо', 'под', 'пра', 'про', 'при', 'пре', 'при', 'пре', 'па', 'по'],
            'и': ['испод', 'изо', 'из', 'ис'],
            'о': ['около', 'обез', 'обес', 'обо', 'ото', 'об', 'от'],
            'м': ['междо', 'между', 'меж'],
            'з': ['зако', 'за'],
            'ч': ['через', 'черес', 'чрез', 'чрес'],
            'к': ['кое', 'ку'],
            'н': ['надо', 'низо', 'недо', 'над', 'наи', 'низ', 'нис', 'на', 'не', 'ни'],
            'с': ['сверх', 'среди', 'су', 'со'],
            'д': ['до'],
            'е': ['еже'],
            'р': ['разо', 'раз', 'рас', 'роз', 'рос'],
            'б': ['без', 'бес'],
            'т': ['тре']
        }
    word_without_affix = word
    if len(word) > 3:
        if word[0] in affixArray.keys():
            for affix in affixArray[word[0]]:
                if(word.startswith(affix) and len(word.lstrip(affix)) > 3):
                    word_without_affix = word.lstrip(affix)
                    break
    return word_without_affix


def  Levenshtein_distance(text, pattern):
   """
   Функция расчета расстояния Левинштейна по алгоритму Вагнера-Фишера.

        :param text - текст поиска
            :type str
        :param text - строка для опредления расстояния между ней и текстом поиска
            :type str

        :param:out list
            :type list
                Структура list: 
                    [
                        :param min_value - минимальное количество изменений
                            :type int, 
                        :param end_pos - конечная позиция найденного паттерна в тексте
                            :type int
                    ]
   """
   text_len, pattern_len = len(text), len(pattern)

   current_column = range(pattern_len+1)
   min_value = pattern_len
   end_pos = 0
   for i in range(1, text_len+1):
      previous_column, current_column = current_column, [0]*(pattern_len+1) # !!!
      for j in range(1,pattern_len+1):
         add, delete, change = previous_column[j]+1, current_column[j-1]+1, previous_column[j-1]
         if pattern[j-1] != text[i-1]:
            change += 1
         current_column[j] = min(add, delete, change)

      if min_value > current_column[pattern_len]: # !!!
         min_value = current_column[pattern_len]
         end_pos = i

   return min_value, end_pos

def preproccess_dict(dict, preproccess_function, morph=None, stemmer=None, stop_words=None, word_length=None):
    preproccessed_dict_ = []
    for word in dict:   
        preproccessed_word_ = preproccess_function(word, morph, stemmer, stop_words, word_length)
        if len(preproccessed_word_) != 0:
            l = preproccessed_word_.values()
            p = []
            for item in l:
                p.append(item[0])
            preproccessed_dict_.append((" ").join(p))
    return preproccessed_dict_

def preproccess_default(text, morph=None, stemmer=None, stop_words=None, word_length=None):
    """
    Функция для тривиального препроцессинга. Делает из текста выжимку, удаляя небуквоцифренные знаки, стоп-слова и слова с низкой значимостью для поиска.

        :param text - текст для обработки
            :type str
        :param stop_words (default None) - список стоп-слов
            :type list(str)
        :param word_length (default None or 3) - ограничение по размеру слова для его удаления в случае отсутствия слова в списке стоп-слов
            :type int

        :param:out comment_proccessed_
            :type dict
                Структура comment_proccessed_: 
                    {
                        :param count_ - номер слова в тексте
                            :type str, 
                            :[
                                 :param word_regexed_group_ - преобразованное_слово
                                    :type str, 
                                 :param word_regexed_start - позиция начала слова
                                    :type int, 
                                 :param word_regexed_start - позиция конца слова
                                    :type int
                             ]
                    }
    """
    regex_ = r"\w+[а-яА-ЯёЁa-zA-Z0-9]|\w/umg"
    comment_proccessed_ = {}
    if stop_words == None:
        stop_words = []
    if word_length == None:
        word_length = 3

    comment_regexed_ = re.finditer(regex_, text, re.MULTILINE | re.UNICODE)

    for count_, word_regexed_ in enumerate(comment_regexed_, start=0):
        word_regexed_group_ = word_regexed_.group().lower()
        if (word_regexed_group_ not in stop_words) and len(word_regexed_group_) > word_length:
            comment_proccessed_[str(count_)] = [word_regexed_group_, word_regexed_.start(), word_regexed_.end()]

    return comment_proccessed_

preproccess_dict(["Функция", "для тривиального препроцессинга"], preproccess_default)
def preproccess_morph(text, morph=None, stemmer=None, stop_words=None, word_length=None):
    """
    Функция препроцессинга. Делает из текста выжимку, удаляя небуквоцифренные знаки, стоп-слова и слова с низкой значимостью для поиска. Заменяет слова на их начальную форму

        :param text - текст для обработки
            :type str
        :param morph - анализатор морфов для выделения начальной формы слова
            :type MorphAnalyzer
            :require lib pymorphy2
        :param stop_words (default None) - список стоп-слов
            :type list(str)
        :param word_length (default None or 3) - ограничение по размеру слова для его удаления в случае отсутствия слова в списке стоп-слов
            :type int

        :param:out comment_proccessed_
            :type dict
                Структура comment_proccessed_: 
                    {
                        :param count_ - номер слова в тексте
                            :type str, 
                            :[
                                 :param word_regexed_group_ - преобразованное_слово
                                    :type str, 
                                 :param word_regexed_start - позиция начала слова
                                    :type int, 
                                 :param word_regexed_start - позиция конца слова
                                    :type int
                             ]
                    }
    """
    regex_ = r"\w+[а-яА-ЯёЁa-zA-Z0-9]|\w/umg"
    comment_proccessed_ = {}
    if stop_words == None:
        stop_words = []
    if word_length == None:
        word_length = 3
        
    comment_regexed_ = re.finditer(regex_, text, re.MULTILINE | re.UNICODE)

    for count_, word_regexed_ in enumerate(comment_regexed_, start=0):
        word_regexed_group_ = word_regexed_.group()
        word_morphed_group_ = morph.parse(word_regexed_.group())[0].normal_form
        if (word_morphed_group_ not in stop_words) and len(word_morphed_group_) > word_length:
            comment_proccessed_[str(count_)] = [word_morphed_group_, word_regexed_.start(), word_regexed_.end()]
        else:
            continue
    return comment_proccessed_

def preproccess_stemm(text, morph=None, stemmer=None, stop_words=None, word_length=None):
    """
    Функция препроцессинга. Делает из текста выжимку, удаляя небуквоцифренные знаки, стоп-слова и слова с низкой значимостью для поиска. Удаляет у слов окончания

        :param text - текст для обработки
            :type str
        :param stemmer - стеммер для удаления окончания у слов
            :type SnowballStemmer
            :require lib nltk.stem.snowball
        :param stop_words (default None) - список стоп-слов
            :type list(str)
        :param word_length (default None or 3) - ограничение по размеру слова для его удаления в случае отсутствия слова в списке стоп-слов
            :type int

        :param:out comment_proccessed_
            :type dict
                Структура comment_proccessed_: 
                    {
                        :param count_ - номер слова в тексте
                            :type str, 
                            :[
                                 :param word_regexed_group_ - преобразованное_слово
                                    :type str, 
                                 :param word_regexed_start - позиция начала слова
                                    :type int, 
                                 :param word_regexed_start - позиция конца слова
                                    :type int
                             ]
                    }
    """
    regex_ = r"\w+[а-яА-ЯёЁa-zA-Z0-9]|\w/umg"
    comment_proccessed_ = {}
    if stop_words == None:
        stop_words = []
    if word_length == None:
        word_length = 3
        
    comment_regexed_ = re.finditer(regex_, text, re.MULTILINE | re.UNICODE)

    for count_, word_regexed_ in enumerate(comment_regexed_, start=0):
        word_regexed_group_ = word_regexed_.group()
        if (word_regexed_group_ not in stop_words) and len(word_regexed_group_) > word_length:
            word_stemmed_group_ = stemmer.stem(word_regexed_.group())
            if len(word_stemmed_group_) > word_length:
                comment_proccessed_[str(count_)] = [word_stemmed_group_, word_regexed_.start(), word_regexed_.end()]
            else:
                comment_proccessed_[str(count_)] = [word_regexed_group_, word_regexed_.start(), word_regexed_.end()]
        else:
            continue

    return comment_proccessed_

def preproccess_morph_stemm(text, morph, stemmer, stop_words=None, word_length=None):
    """
    Функция препроцессинга. Делает из текста выжимку, удаляя небуквоцифренные знаки, стоп-слова и слова с низкой значимостью для поиска. Приводит слова к начальной форме и удаляет у слов окончания

        :param text - текст для обработки
            :type str
        :param morph - анализатор морфов для выделения начальной формы слова
            :type MorphAnalyzer
            :require lib pymorphy2
        :param stemmer - стеммер для удаления окончания у слов
            :type SnowballStemmer
            :require lib nltk.stem.snowball
        :param stop_words (default None) - список стоп-слов
            :type list(str)
        :param word_length (default None or 3) - ограничение по размеру слова для его удаления в случае отсутствия слова в списке стоп-слов
            :type int

        :param:out comment_proccessed_
            :type dict
                Структура comment_proccessed_: 
                    {
                        :param count_ - номер слова в тексте
                            :type str, 
                            :[
                                 :param word_regexed_group_ - преобразованное_слово
                                    :type str, 
                                 :param word_regexed_start - позиция начала слова
                                    :type int, 
                                 :param word_regexed_start - позиция конца слова
                                    :type int
                             ]
                    }
    """
    regex_ = r"\w+[а-яА-ЯёЁa-zA-Z0-9]|\w/umg"
    comment_proccessed_ = {}
    if stop_words == None:
        stop_words = []
    if word_length == None:
        word_length = 3
        
    comment_regexed_ = re.finditer(regex_, text, re.MULTILINE | re.UNICODE)

    for count_, word_regexed_ in enumerate(comment_regexed_, start=0):
        word_regexed_group_ = word_regexed_.group()
        if (word_regexed_group_ not in stop_words) and len(word_regexed_group_) > word_length:
            word_morphed_group_ = morph.parse(word_regexed_.group())[0].normal_form
            if (word_morphed_group_ not in stop_words) and len(word_morphed_group_) > word_length:
                word_morphed_stemmed_group_ = stemmer.stem(word_morphed_group_)
                if len(word_morphed_stemmed_group_) > word_length:
                    comment_proccessed_[str(count_)] = [word_morphed_stemmed_group_, word_regexed_.start(), word_regexed_.end()]
                else:
                    comment_proccessed_[str(count_)] = [word_morphed_stemmed_group_, word_regexed_.start(), word_regexed_.end()]
            else:
                comment_proccessed_[str(count_)] = [word_morphed_group_, word_regexed_.start(), word_regexed_.end()]
        else:
            continue

    return comment_proccessed_

def preproccess_morph_stemm_affix(text, morph, stemmer, stop_words=None, word_length=None):
    """
    Функция препроцессинга. Делает из текста выжимку, удаляя небуквоцифренные знаки, стоп-слова и слова с низкой значимостью для поиска. Приводит слова к начальной форме, удаляет у слов окончания и грубо (не по правилам словообразования) удаляет первую приставку слова

        :param text - текст для обработки
            :type str
        :param morph - анализатор морфов для выделения начальной формы слова
            :type MorphAnalyzer
            :require lib pymorphy2
        :param stemmer - стеммер для удаления окончания у слов
            :type SnowballStemmer
            :require lib nltk.stem.snowball
        :param stop_words (default None) - список стоп-слов
            :type list(str)
        :param word_length (default None or 3) - ограничение по размеру слова для его удаления в случае отсутствия слова в списке стоп-слов
            :type int

        :param:out comment_proccessed_
            :type dict
                Структура comment_proccessed_: 
                    {
                        :param count_ - номер слова в тексте
                            :type str, 
                            :[
                                 :param word_regexed_group_ - преобразованное_слово
                                    :type str, 
                                 :param word_regexed_start - позиция начала слова
                                    :type int, 
                                 :param word_regexed_start - позиция конца слова
                                    :type int
                             ]
                    }
    """
    regex_ = r"\w+[а-яА-ЯёЁa-zA-Z0-9]|\w/umg"
    comment_proccessed_ = {}
    if stop_words == None:
        stop_words = []
    if word_length == None:
        word_length = 3
        
    comment_regexed_ = re.finditer(regex_, text, re.MULTILINE | re.UNICODE)

    for count_, word_regexed_ in enumerate(comment_regexed_, start=0):
        word_regexed_group_ = word_regexed_.group()
        if (word_regexed_group_ not in stop_words) and len(word_regexed_group_) > word_length:
            word_morphed_group_ = morph.parse(word_regexed_.group())[0].normal_form
            if (word_morphed_group_ not in stop_words) and len(word_morphed_group_) > word_length:
                word_morphed_stemmed_group_ = stemmer.stem(word_morphed_group_)
                if len(word_morphed_stemmed_group_) > word_length:
                    word_without_affix_group_ = preproccess_delete_affix(word_morphed_stemmed_group_)
                    if len(word_morphed_stemmed_group_) > word_length:
                        comment_proccessed_[str(count_)] = [word_without_affix_group_, word_regexed_.start(), word_regexed_.end()]
                    else:
                        comment_proccessed_[str(count_)] = [word_morphed_stemmed_group_, word_regexed_.start(), word_regexed_.end()]
                else:
                    comment_proccessed_[str(count_)] = [word_morphed_stemmed_group_, word_regexed_.start(), word_regexed_.end()]
            else:
                comment_proccessed_[str(count_)] = [word_morphed_group_, word_regexed_.start(), word_regexed_.end()]
        else:
            continue

    return comment_proccessed_

def search_key_word_substring(key_word, text, accuracy=None):
    """
    Функция поиска ключевого слова как подстроки передаваемой строки.

        :param key_word - ключевое слово (словосочетание)
            :type str
        :param text - текст для обработки
            :type str

        :param:out list
            :type list
                Структура list:
                [
                    :param len(matches_)//2 - количество вхождений слова(словосочетания) в текст
                        :type int, 
                    :param list - вхождения слова(словосочетания) в текст. Количество вхождений может быть различным.
                        :type list,    
                        [
                            :param start_pos - начало вхождения
                                :type int,
                            :param end_pos - конец вхождения
                                :type int
                        ]
                ]
    """
    matches_ = []
    key_subwords_ = key_word.split(" ")

    if len(key_subwords_) == 1:
        for word_ in text.values():
            if word_[0].find(key_word) != -1:
                matches_.extend([word_[1], word_[2]])

        return (len(matches_), matches_)
    else:
        coef = 0
        sub_match_ = []
        for key_subword_ in key_subwords_:
            for word_ in text.values():
                if word_[0].find(key_subword_) != -1:
                    coef += 1
                    sub_match_.extend([word_[1], word_[2]])
        if coef == len(key_subwords_):
            matches_.extend(sub_match_)
        return (len(matches_)//2, matches_)
    
def search_key_word_strict(key_word, text, accuracy=None):
    """
    Функция поиска строгого поиск ключевого слова. При передаче словосочетаний будет попытка найти именно эти слвоа, но по отдельности

        :param key_word - ключевое слово (словосочетание)
            :type str
        :param text - текст для обработки
            :type str

        :param:out list
            :type list
                Структура list:
                [
                    :param len(matches_)//2 - количество вхождений слова(словосочетания) в текст
                        :type int, 
                    :param list - вхождения слова(словосочетания) в текст. Количество вхождений может быть различным.
                        :type list,    
                        [
                            :param start_pos - начало вхождения
                                :type int,
                            :param end_pos - конец вхождения
                                :type int
                        ]
                ]
    """
    matches_ = []
    key_subwords_ = key_word.split(" ")

    if len(key_subwords_) == 1:
        for word_ in text.values():
            regex_ = r"\b" + key_word + r"\b"
            match_ =  re.finditer(regex_, word_[0], re.UNICODE | re.MULTILINE)
            for count_, match_item_ in enumerate(match_, start=0):
                matches_.extend([word_[1], word_[2]])
        return (len(matches_), matches_)
    else:
        coef = 0
        sub_match_ = []
        for key_subword_ in key_subwords_:
            for word_ in text.values():
                regex_ = r"\b" + key_subword_ + r"\b"
                match_ =  re.finditer(regex_, word_[0], re.UNICODE | re.MULTILINE)
                for count_, match_item_ in enumerate(match_, start=0):
                    sub_match_.extend([word_[1], word_[2]])
        matches_.extend(sub_match_)
        return (len(matches_)//2, matches_)

def search_key_word_unstrict(key_word, text, accuracy=3):
    """
    Функция нечеткого поиска ключевого слова. При передаче словосочетаний будет попытка найти именно эти слвоа, но по отдельности. Если слово маленькое, будет производиться поиск слова как подстроки

        :param key_word - ключевое слово (словосочетание)
            :type str
        :param text - текст для обработки
            :type str
        :param accuracy(default 3) - коэффициент четкости поиска
            :type int

        :param:out list
            :type list
                Структура list:
                [
                    :param len(matches_)//2 - количество вхождений слова(словосочетания) в текст
                        :type int, 
                    :param list - вхождения слова(словосочетания) в текст. Количество вхождений может быть различным.
                        :type list,    
                        [
                            :param start_pos - начало вхождения
                                :type int,
                            :param end_pos - конец вхождения
                                :type int
                        ]
                ]
    """
    matches_ = []
    key_subwords_ = key_word.split(" ")
    if len(key_subwords_) == 1:
         for word_ in text.values():
            if len(key_word) <= 4:
                if word_[0].find(key_word) != -1:
                    matches_.extend([word_[1], word_[2]])
                else:
                    continue
            else:
                match_ = Levenshtein_distance(word_[0], key_word)[0]
                if match_ <= accuracy:
                    matches_.extend([word_[1], word_[2]])
                else:
                    continue
    else:
        coef = 0
        sub_match_ = []
        for key_subword_ in key_subwords_:
            for word_ in text.values():
                if len(key_word) < 4 and len(key_subword_) + accuracy > len(word[0]):
                    if word_[0].find(key_subword_) != -1:
                        sub_match_.extend([word_[1], word_[2]])
                        coef += 1
                    else:
                        continue
                else:
                    match_ = Levenshtein_distance(word_[0], key_subword_)[0]
                    if match_ <= accuracy:
                        sub_match_.extend([word_[1], word_[2]])
                        coef += 1
                    else:
                        continue
        if coef == len(key_subwords_):
            matches_.extend(sub_match_)

    return (len(matches_)//2, matches_)


def search_pipeline(text, dict1, preproccess_function, search_function, morph=None, stemmer=None, word_length=None, accuracy=None, stop_words=None):
    preproccessed_text_ = preproccess_function(text, morph, stemmer, stop_words, word_length)
    result = {}
    for key_word_ in dict1:
        sub_result = search_function(key_word_, preproccessed_text_, accuracy)
        if sub_result[0] != 0:
            result[key_word_] = sub_result[1]
    return (len(result), result)

def match_marking(text, matches):
    res_ = text
    true_length = len(text)
    kwords = []
    for match_ in matches.items():
        kwords.append(match_[0])
        for count_, sub_match_ in enumerate(match_[1], start=0):
            print(count_, sub_match_)
            if (count_+1)%2 == 0:
                g = len(res_) - true_length
                res_ = res_[:match_[1][count_-1]+g] + '<span class="text-browser__comment__list__text--triggered" keyword="' + match_[0] + '">' + res_[match_[1][count_-1]+g:match_[1][count_]+g] + '</span>' + res_[match_[1][count_]+g:]
    return (res_, "///".join(kwords))


#sub_match_ = match_[1]
 #       if len(match_[1]) == 2:
   #            res_ = text[:sub_match_[0]] + "<span class='' keyword='" + match_[0] + "'>" + text[sub_match_[0]:sub_match_[1]] + "</span>" + text[sub_match_[1]:]
   #     else:
     #       for count_ in range(0, len(match_[1]), 2):
      #          print(sub_match_[count_-1], sub_match_[count_])
       #         res_ = text[:sub_match_[count_-1]] + "<span class='' keyword='" + match_[0] + "'>" + text[sub_match_[count_-1]:sub_match_[count_]] + "</span>" + text[sub_match_[count_]:]
























































def distance(a, b):
   "Calculates the Levenshtein distance between a and b."
   n, m = len(a), len(b)
   if n > m:
      # Make sure n <= m, to use O(min(n,m)) space
      a, b = b, a
      n, m = m, n

   current_column = range(n+1) # Keep current and previous column, not entire matrix
   for i in range(1, m+1):
      previous_column, current_column = current_column, [i]+[0]*n
      for j in range(1,n+1):
         add, delete, change = previous_column[j]+1, current_column[j-1]+1, previous_column[j-1]
         if a[j-1] != b[i-1]:
            change += 1
         current_column[j] = min(add, delete, change)

   return current_column[n]

def distance_2(text, pattern):
   "Calculates the Levenshtein distance between text and pattern."
   text_len, pattern_len = len(text), len(pattern)

   current_column = range(pattern_len+1)
   min_value = pattern_len
   end_pos = 0
   for i in range(1, text_len+1):
      previous_column, current_column = current_column, [0]*(pattern_len+1) # !!!
      for j in range(1,pattern_len+1):
         add, delete, change = previous_column[j]+1, current_column[j-1]+1, previous_column[j-1]
         if pattern[j-1] != text[i-1]:
            change += 1
         current_column[j] = min(add, delete, change)

      if min_value > current_column[pattern_len]: # !!!
         min_value = current_column[pattern_len]
         end_pos = i

   return min_value, end_pos

def distance_3(text, pattern):
   min_value, end_pos = distance_2(text, pattern)
   min_value, start_pos = distance_2(text[end_pos-1::-1], pattern[::-1])
   start_pos = end_pos - start_pos
   return min_value, start_pos, end_pos, text[start_pos:end_pos], pattern
#Поиск основы слова как подстроки
#1504coms --- 1.227s
# in - (dict::dictionary, comment::string, morph::pymorphy2.MorphAnalyzer, stemmer::SnowballStemmer); out - (len::int, matches::dictionary) or ()
    # matches[key_word]::array == [start_pos::int, end_pos::int] or [[start_pos::int, end_pos::int], [start_pos::int, end_pos::int], [start_pos::int, end_pos::int], ...]
def search_word_base(dict1, comment, morph, stemmer):
    matches = {}
    regex = r"\w+[а-яА-ЯёЁa-zA-Z0-9]|\w/umg"
    for key_word in dict1:
        matches[key_word] = []
        cur_key_ph = re.findall(regex, key_word)
        if len(cur_key_ph) == 1:
            pos = comment.find(stemmer.stem(morph.parse(cur_key_ph[0])[0].normal_form))
            if pos != -1:
                matches[key_word].append([pos, pos + len(cur_key_ph[0])])
            else:
                matches.pop(key_word.lower())
        else:
            sub_match = []
            p = 0
            for key_subword in cur_key_ph:
                c = comment.find(stemmer.stem(morph.parse(key_subword)[0].normal_form))
                if c == -1:
                    matches.pop(key_word.lower())
                    p+=c
                    break
                else:
                    sub_match.append([c, c + len(key_subword)])
                    p+=1
            if p == len(cur_key_ph):
                matches[key_word] = sub_match
    if len(matches) == 0:
        return ()
    else:
        return  (len(matches), matches)
#Поиск строгого вхождения слова
#1504coms --- 0.084s
# in - (dict::dictionary, comment::string); out - (len::int, matches::dictionary) or ()
    # matches[key_word]::array == [start_pos::int, end_pos::int]
def search_word_strict(dict, comment):
    matches = {}
    regex = ""
    comment = comment.lower()
    for key_word in dict:
        key_word = key_word.lower()
        matches[key_word] = []
        regex = r"\b" + key_word + r"\b"
        match =  re.finditer(regex, comment, re.UNICODE | re.MULTILINE)
        for cur_match in match:
            matches[key_word].append([cur_match.start(), cur_match.end()])
        if len(matches[key_word]) == 0:
            matches.pop(key_word)

    if len(matches) == 0:
        return ()
    else:
        return  (len(matches), matches)