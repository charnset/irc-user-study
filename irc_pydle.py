import argparse
import os
import random
import re
import string
import spacy
import pydle
from puppeteer import Extractions, MessageObservation
from bots import print_args, load_puppeteer

random.seed(0)

C = list(range(999999, 9999999)) #range(999,999, 9,999,999)
random.shuffle(C)

nlp = spacy.load("en_core_web_sm")

room = {}

def get_simple_sentences(msg):
	""" Split a massage by punctuations
		if the split sentence is compound (FANBOYS: For, And, Nor, But, Or, Yet, So)
		then segment it into multiple simple sentences
		a simple sentence is a sequence of word in which 
		its dependency tree contains at least one VERB token and one SUBJ token (nsubj, csubj)
	"""
	sentences = set()
	split_msg = re.split("[" + string.punctuation + "]+", msg)
	split_msg = [s.strip().lower() for s in split_msg if s.strip()]
	# print(split_msg)

	if len(split_msg) > 1:
		sentences.update(split_msg)

	for m in split_msg:
		text = nlp(m)
		conj_idx = []
		for token in text:
			if token.text in ["for", "and", "nor", "but", "or", "yet", "so"]: #CONJUNCTIONS: FANBOYS
				conj_idx.append(token.i)

		# print(conj_idx)

		clauses = []
		if conj_idx:
			span = text[:conj_idx[0]]
			cl = ' '.join([t.text for t in span])
			clauses.append(cl)

		for j, idx in enumerate(conj_idx):
			start = conj_idx[j]
			end = conj_idx[j+1] if j+1 < len(conj_idx) else None
			span = text[start:end] if j+1 < len(conj_idx) else text[start:]
			has_subj = False
			has_verb = False
			for token in span:
				if token.dep_ == "nsubj" or token.dep_ == "csubj":
					has_subj = True
				if token.pos_ == "AUX" or token.pos_ == "VERB":
					has_verb = True
				if has_subj and has_verb:
					break
			if has_subj and has_verb:
				cl = ' '.join([t.text for t in span[:]])
				clauses.append(cl)
			else:
				phrase = ' ' + ' '.join([t.text for t in span])
				clauses[-1] += phrase

		clauses = [cl.strip() for cl in clauses if cl.strip()]
		# print(clauses)
		sentences.update(clauses)

	return list(sentences)

def get_agenda_state_log(agenda_name, at_state):
	"""	Log for each agenda, 
		which state we are at, 
		how much confidence we are at that state, 
		how many consecutive turns we have been idle
	"""
	return "{{agenda: {}, at_state: {}, prob: {:.3f}, been_idle: {}}}".format(agenda_name, at_state[0], at_state[1], at_state[2])

# Puppeteer bot.
class MyOwnBot(pydle.Client):
	def __init__(self,
		nickname,
		agenda_dir,
		agenda_names,
		nlu_data_dir,
		fallback_nicknames=[],
		username=None,
		realname=None,
		eventloop=None,
		**kwargs):
		super().__init__(
			nickname,
			fallback_nicknames,
			username,
			realname,
			eventloop,
			**kwargs)
		# Load Puppeteer
		self._puppeteer = load_puppeteer(agenda_dir, agenda_names, nlu_data_dir)
		self._conversation = []
		self._actions = []
		self._extractions = Extractions()

	async def on_connect(self):
		channel = "#user-study-" + str(C.pop())
		room[self.nickname] = channel
		await self.join(channel)

	async def on_join(self, channel, user):
		print("{} joined {}".format(user, channel), flush=True)
		if "MyBot" in user:
			await self.set_mode(channel, "+H", "30:12h")
			print("/MODE {} +H 30:12h".format(channel), flush=True)

	async def on_message(self, target, source, message):
		# don't respond to our own messages, as this leads to a positive feedback loop
		if source != self.nickname:
			msg = [MessageObservation(message)]
			simple_sentences = get_simple_sentences(message)
			print(simple_sentences)
			simple_msg = [MessageObservation(sent) for sent in simple_sentences]
			msg += simple_msg
			actions, extractions = self._puppeteer.react(msg, self._extractions)

			print(self._puppeteer.log)

			cur_active_agenda_names = self._puppeteer.get_active_agenda_names()
			# print(cur_active_agenda_names)
			cur_states = self._puppeteer.get_active_states(cur_active_agenda_names)
			# print(cur_states)

			if actions:
				self._actions.append(actions)
			if extractions:
				self._extractions.update(extractions)

			#Collect conversation: text + actions (filled the placeholder with extractions)
			phisher_text = "0: " + message
			self._conversation.append(phisher_text)
			puppeteer_actions = []
			for act in actions:
				t = act._text
				#replace placeholder with extractions (if applicable)
				for e in extractions.names:
					if e.isupper(): #placeholder is the key with all uppercase letters
						t = t.replace(e, extractions.extraction(e))
				puppeteer_actions.append(t)
			if len(puppeteer_actions) >  0:
				puppeteer_message = ' '.join(puppeteer_actions)
				puppeteer_text = "1: " + puppeteer_message
				self._conversation.append(puppeteer_text)
				await self.message(target, "\u0003" + "12" + puppeteer_message) #blue
			else:
				#Debugging message
				await self.message(target, "\u0003" + "04" + \
				"       DEBUG:   " + \
				"*** No Action Detected ***") #red

			#Debugging message
			if cur_states:
				for agenda_name, at_state in cur_states.items():
					await self.message(target, "\u0003" + "05" + \
						"       DEBUG:   " + \
						"ACTIVE = {}".format(get_agenda_state_log(agenda_name, at_state)))

def main_event(args):
	print(args)
	server = args.server
	port = int(args.port)
	n = int(args.num_bots)
	agenda_dir = args.agenda_dir
	agenda_names = args.agenda_names
	nlu_data_dir = args.nlu_data_dir
	#print(server, port, n)
	pool = pydle.ClientPool()
	for i in range(n):
		client = MyOwnBot("MyBot" + str(i), agenda_dir, agenda_names, nlu_data_dir)
		pool.connect(client, server, port)

	# This will make sure all clients are treated in a fair way priority-wise.
	pool.handle_forever()

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--server", type=str, help="server")
	parser.add_argument("--port", type=str, help="port")
	parser.add_argument("--num_bots", type=str, help="number of bots")
	parser.add_argument("--agenda_dir", type=str, help='path to agenda directory')
	parser.add_argument("--agenda_names", nargs='+', type=str, help='list of agenda names')
	parser.add_argument("--nlu_data_dir", type=str, help='path to NLU training data directory')
	args = parser.parse_args()
	main_event(args)
