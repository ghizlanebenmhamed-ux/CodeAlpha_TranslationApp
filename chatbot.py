"""University FAQ chatbot: NLTK tokenization, TF-IDF, cosine similarity."""
import json
import re
import tkinter as tk
from pathlib import Path
from tkinter import scrolledtext
from nltk.tokenize import RegexpTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class FAQEngine:
    def __init__(self):
        self.faqs = json.loads(Path(__file__).with_name('faqs.json').read_text(encoding='utf-8'))
        self.tokenizer = RegexpTokenizer(r'[a-z0-9]+')
        self.questions, self.answers = [], []
        for faq in self.faqs:
            for question in faq['questions']:
                self.questions.append(question)
                self.answers.append(faq['answer'])
        self.vectorizer = TfidfVectorizer(tokenizer=self.preprocess, token_pattern=None,
                                        lowercase=False, ngram_range=(1, 2))
        self.vectors = self.vectorizer.fit_transform(self.questions)

    def preprocess(self, text):
        return self.tokenizer.tokenize(text.lower())

    def reply(self, message):
        cleaned = ' '.join(self.preprocess(message))
        if not cleaned:
            return 'Please type a university question.'
        if cleaned in {'hi', 'hello', 'hey', 'good morning', 'good evening'}:
            return 'Hello! Ask about courses, exams, grades, scholarships, or campus services. Type help for topics.'
        if cleaned in {'thanks', 'thank you', 'thank you very much'}:
            return "You're welcome! Ask another question whenever you like."
        if cleaned in {'bye', 'goodbye'}:
            return 'Goodbye! Good luck with your studies.'
        if cleaned in {'help', 'topics', 'what can you do'}:
            return 'Available topics: ' + ', '.join(f['topic'] for f in self.faqs) + '.'
        vector = self.vectorizer.transform([message])
        scores = cosine_similarity(vector, self.vectors)[0]
        index = int(scores.argmax())
        if vector.nnz == 0 or scores[index] < 0.30:
            return 'I could not find a reliable FAQ answer. Please rephrase your question, or type help for available topics.'
        return self.answers[index]

class ChatbotApp:
    def __init__(self, root):
        self.engine = FAQEngine()
        self.root = root
        root.title('University FAQ Chatbot')
        root.geometry('760x620')
        root.minsize(520, 440)
        root.configure(bg='#F5F3F8')
        root.columnconfigure(0, weight=1)
        root.rowconfigure(2, weight=1)
        header = tk.Frame(root, bg='#4C356A', padx=20, pady=18)
        header.grid(row=0, column=0, sticky='ew')
        tk.Label(header, text='University FAQ Chatbot', font=('Segoe UI', 20, 'bold'),
                 bg='#4C356A', fg='white').pack(anchor='w')
        tk.Label(header, text='Ask about university services', font=('Segoe UI', 11),
                 bg='#4C356A', fg='#E9DFF5').pack(anchor='w')
        tk.Label(root, text='Demo FAQs: confirm policies with your university.',
                 bg='#F5F3F8', fg='#655B70').grid(row=1, column=0, pady=(10, 0))
        self.chat = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=('Segoe UI', 11),
                                             bg='white', padx=15, pady=15, state=tk.DISABLED)
        self.chat.grid(row=2, column=0, sticky='nsew', padx=16, pady=12)
        self.chat.tag_configure('user', foreground='#4C356A', font=('Segoe UI', 11, 'bold'))
        self.chat.tag_configure('bot', foreground='#24705B', font=('Segoe UI', 11, 'bold'))
        bottom = tk.Frame(root, bg='#F5F3F8')
        bottom.grid(row=3, column=0, sticky='ew', padx=16, pady=(0, 12))
        bottom.columnconfigure(0, weight=1)
        self.entry = tk.Entry(bottom, font=('Segoe UI', 12), bg='white', fg='#292333',
                              insertbackground='#292333')
        self.entry.grid(row=0, column=0, sticky='ew', ipady=10, padx=(0, 10))
        self.entry.bind('<Return>', self.send_message)
        self.send_button = tk.Button(bottom, text='Send', command=self.send_message,
                                     bg='#4C356A', fg='white', font=('Segoe UI', 11, 'bold'),
                                     padx=20, pady=8)
        self.send_button.grid(row=0, column=1)
        tk.Button(root, text='Clear chat', command=self.clear_chat,
                  bg='#E8E1F0', fg='#4C356A').grid(row=4, column=0, sticky='w', padx=16, pady=(0, 12))
        self.welcome()
        self.entry.focus_set()

    def append_message(self, speaker, message, tag):
        self.chat.configure(state=tk.NORMAL)
        self.chat.insert(tk.END, speaker + '\n', tag)
        self.chat.insert(tk.END, message + '\n\n')
        self.chat.configure(state=tk.DISABLED)
        self.chat.see(tk.END)

    def welcome(self):
        self.append_message('Chatbot', 'Hello! Try: How can I check my grades? Type help for topics.', 'bot')

    def send_message(self, event=None):
        message = self.entry.get().strip()
        if not message:
            self.entry.focus_set()
            return
        self.entry.delete(0, tk.END)
        self.append_message('You', message, 'user')
        try:
            answer = self.engine.reply(message)
        except Exception as error:
            print('Processing error:', error)
            answer = 'A processing error occurred. Please check the terminal and try again.'
        self.append_message('Chatbot', answer, 'bot')
        self.entry.focus_set()

    def clear_chat(self):
        self.chat.configure(state=tk.NORMAL)
        self.chat.delete('1.0', tk.END)
        self.chat.configure(state=tk.DISABLED)
        self.welcome()
        self.entry.focus_set()

if __name__ == '__main__':
    root = tk.Tk()
    ChatbotApp(root)
    root.mainloop()
