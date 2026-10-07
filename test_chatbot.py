import unittest
from unittest.mock import Mock
from chatbot import FAQEngine, ChatbotApp

class ChatbotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = FAQEngine()

    def test_all_stored_questions(self):
        for faq in self.engine.faqs:
            for question in faq['questions']:
                with self.subTest(question=question):
                    self.assertEqual(self.engine.reply(question), faq['answer'])

    def test_examples_and_fallback(self):
        for question, fragment in [('How can I check my grades?', 'grades'),
                                   ('I forgot my password', 'reset'),
                                   ('How do I borrow books?', 'student card'),
                                   ('How can I apply for a scholarship?', 'scholarship'),
                                   ('How do I find an internship?', 'internship')]:
            self.assertIn(fragment, self.engine.reply(question))
        self.assertIn('could not find', self.engine.reply('quantum penguin weather'))
        self.assertIn('Hello', self.engine.reply('HELLO!'))

    def make_app(self, message):
        app = ChatbotApp.__new__(ChatbotApp)
        app.engine = self.engine
        app.entry = Mock()
        app.entry.get.return_value = message
        app.append_message = Mock()
        return app

    def test_send_handler_displays_answer(self):
        app = self.make_app('How can I check my grades?')
        app.send_message()
        self.assertEqual(app.append_message.call_count, 2)
        self.assertEqual(app.append_message.call_args.args,
                         ('Chatbot', self.engine.reply('How can I check my grades?'), 'bot'))
        app.entry.delete.assert_called_once()

    def test_enter_uses_same_handler(self):
        app = self.make_app('I forgot my password')
        app.send_message(event=Mock())
        self.assertIn('reset', app.append_message.call_args.args[1])

    def test_empty_send(self):
        app = self.make_app('   ')
        app.send_message()
        app.append_message.assert_not_called()

    def test_error_still_displays_response(self):
        app = self.make_app('hello')
        app.engine = Mock()
        app.engine.reply.side_effect = RuntimeError('test error')
        app.send_message()
        self.assertIn('processing error', app.append_message.call_args.args[1])

    def test_clear_resets_conversation(self):
        app = self.make_app('')
        app.chat = Mock()
        app.clear_chat()
        app.chat.delete.assert_called_once_with('1.0', 'end')
        self.assertIn('Hello', app.append_message.call_args.args[1])

if __name__ == '__main__':
    unittest.main(verbosity=2)
