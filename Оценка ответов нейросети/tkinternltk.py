import tkinter as tk
from tkinter import scrolledtext
from nltk.translate.bleu_score import corpus_bleu
from rouge import Rouge
from nltk.translate.meteor_score import meteor_score
from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt')
nltk.download('wordnet')

# Определим функцию для вывода результатов в окно tkinter
def update_text(text):
    text_area.insert(tk.END, text)

def load_data_from_file(file_path):
    questions = []
    reference_answers = []

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

        for line in lines:
            # Разделение строки на вопрос и ответ по символу ":"
            parts = line.strip().split(':')
            if len(parts) == 2:
                questions.append(parts[0])  # Первая часть строки - вопрос
                reference_answers.append(parts[1])  # Вторая часть строки - ответ

    return questions, reference_answers

def load_data_answers_from_file(file_path_2):
    answers = []

    with open(file_path_2, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        
        for line in lines:
            answers.append(line.strip())
    
    return answers

def tokenize_text(text):
    return text.split() 

def evaluate_answers(questions, reference_answers, answers):
    # Подготовка эталонных и сгенерированных ответов в формате, необходимом для библиотеки Rouge
    rouge = Rouge()
    references = reference_answers
    candidates = answers

    #Вычисление BLEU Score с учетом формата NLTK
    bleu_score = corpus_bleu([[answer.split()] for answer in reference_answers], [answer.split() for answer in answers])
    #Вычиление ROUGE Scores
    rouge_scores = rouge.get_scores(candidates, references, avg=True)

    # Предварительная токенизация гипотез
    tokenized_candidates = [tokenize_text(candidate) for candidate in candidates]
    # Предварительная токенизация эталонных ответов
    tokenized_references = [tokenize_text(reference) for reference in references]

    # Вычисление METEOR score
    meteor_scores = [meteor_score([ref], can) for ref, can in zip(tokenized_references, tokenized_candidates)]
    meteor_avg = sum(meteor_scores) / len(meteor_scores)

    return bleu_score, rouge_scores, meteor_avg

file_path_2 = 'Ответы chat gpt.txt'
file_path = 'Q&A.txt'

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Model Evaluation Results")
    
    text_area = scrolledtext.ScrolledText(root, width=100, height=30)
    text_area.pack(expand=True, fill='both')

    questions, reference_answers = load_data_from_file(file_path)
    answers = load_data_answers_from_file(file_path_2)

    bleu_score, rouge_scores, meteor_avg = evaluate_answers(questions, reference_answers, answers)

    if bleu_score <= 0.1:
        update_text(f"BLEU Score: {bleu_score}. Генерируемые ответы совсем не соответствуют эталонным ответам. Ответы содержат много несвязанных фраз, неверных последовательностей слов, их смысл не ясен или даже искажен. В ответах может быть большое количество дополнительной информации, которая не имеет отношения к контексту или запросу.\n")
    elif 0.1 < bleu_score < 0.3:
        update_text(f"BLEU Score: {bleu_score}. Сгенерированные ответы содержат огромное количество отклонений от эталонных ответов. Несмотря на то, что в некоторых ответах могут присутствовать некоторые общие элементы с эталонами, большая часть текста совершенно не совпадает с ожидаемым или требуемым.\n")
    elif 0.3 < bleu_score < 0.5:
        update_text(f"BLEU Score: {bleu_score}. Генерируемые ответы имеют некоторое сходство с эталонными ответами, но это сходство ограничено. В ответах могут присутствовать некоторые точные фразы или последовательности слов из эталонов, но в целом сгенерированный текст значительно отличается от ожидаемого.\n")
    elif 0.5 < bleu_score < 0.7:
        update_text(f"BLEU Score: {bleu_score}. Ответы начинают иметь более существенное сходство с эталонами. Модель может воспроизводить некоторые фразы и выражения из эталонных ответов, но всё ещё есть значительные отклонения и неточности в тексте.\n")
    elif 0.7 < bleu_score < 0.9:
        update_text(f"BLEU Score: {bleu_score}. Генерируемые ответы достаточно точно соответствуют эталонным ответам. Модель успешно воспроизводит многие фразы и последовательности слов из эталонов, но могут быть небольшие отклонения и несовпадения.\n")
    elif 0.9 < bleu_score < 1:
        update_text(f"BLEU Score: {bleu_score}. Высокий BLEU Score свидетельствует о том, что сгенерированные ответы практически идентичны эталонным ответам. Модель точно воспроизводит фразы и выражения из эталонов, с минимальными отклонениями и несовпадениями. Однако, высокий BLEU Score не гарантирует семантическое или контекстуальное соответствие ответов.\n")

    for key, value in rouge_scores.items():
        update_text(f"{key}: 'r': {value['r']}, 'p': {value['p']}, 'f': {value['f']}\n")

    update_text('Показатели r, p и f отражают процент пересечения последовательностей слов или словосочетаний между сгенерированными и эталонными ответами (r), точность таких пересечений (p) и гармоническое среднее между полнотой и точностью пересечения (f). Показатели принимают значения от 0 до 1. Следовательно, чем выше показатели каждого ROUGE, тем лучше ответы нейро-сети семантически и контекстуально подходят к эталонным ответам.\n')

    update_text(f"METEOR Score: {meteor_avg}\n")

    if meteor_avg <= 0.1:
        update_text(f"METEOR Score: {meteor_avg}. Генерируемые ответы совсем не соответствуют эталонным ответам с точки зрения семантики. Слова и фразы в ответах сильно расходятся с эталонами, их смысл не распознается или даже искажен.\n")
    elif 0.1 < meteor_avg < 0.3:
        update_text(f"METEOR Score: {meteor_avg}. Сгенерированные ответы имеют очень низкую семантическую схожесть с эталонными ответами. В тексте могут быть случайные совпадения слов или фраз, но в целом ответы значительно отличаются от ожидаемых или требуемых.\n")
    elif 0.3 < meteor_avg < 0.5:
        update_text(f"METEOR Score: {meteor_avg}. Генерируемые ответы имеют некоторое сходство с эталонными ответами, но оно ограничено и несовершенно. Модель может содержать некоторые слова или фразы из эталонов, но в целом контекст и смысл ответов существенно отличается.\n")
    elif 0.5 < meteor_avg < 0.7:
        update_text(f"METEOR Score: {meteor_avg}. Ответы начинают иметь заметную семантическую схожесть с эталонными ответами. Модель успешно улавливает некоторую информацию из исходных вопросов и инкорпорирует ее в ответы. В тексте могут быть учтены некоторые синонимы и различные формы слов.\n")
    elif 0.7 < meteor_avg < 0.9:
        update_text(f"METEOR Score: {meteor_avg}. Генерируемые ответы достаточно точно соответствуют эталонным ответам с точки зрения семантики. Модель успешно учитывает многие слова и фразы из эталонов, с минимальными отклонениями и несовпадениями.\n")
    elif 0.9 < meteor_avg < 1:
        update_text(f"METEOR Score: {meteor_avg}. Высокий METEOR Score указывает на то, что сгенерированные ответы практически идентичны эталонным ответам с точки зрения семантики. Модель успешно генерирует разнообразные формы ответов, сохраняя их смысл и контекст, даже если они не совпадают слово в слово.\n")

    root.mainloop()