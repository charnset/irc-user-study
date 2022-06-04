import argparse
import os
from typing import List
import numpy as np
from puppeteer import Agenda, Extractions, MessageObservation, Puppeteer
from puppeteer.trigger_detectors.loader import MyTriggerDetectorLoader

AGENDA_NAMES = ["get_shipment", "get_payment", "get_website"]
#AGENDA_NAMES = ["get_shipment", "get_payment"]
DIR = "../ppt-control/"
AGENDA_DIR = DIR + "agendas"
NLI_DATA_DIR = DIR + "nli_premises"
NLU_DATA_DIR = DIR + "nlu_training_data"

class TestConversation:
    def __init__(self, agendas: List[Agenda]):
        self._puppeteer = Puppeteer(agendas, plot_state=False)
        self._conversation = []
        self._actions = []
        self._extractions = Extractions()
        np.random.seed(0)

    def say(self, text):
        print("-"*40)
        print("You said: %s" % text)

        actions, extractions = self._puppeteer.react([MessageObservation(text)], self._extractions)

        if actions:
            self._actions.append(actions)
        if extractions:
            self._extractions.update(extractions)

        #Collect conversation: text + actions (filled the placeholder with extractions)
        phisher_text = "0: " + text
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
            puppeteer_text = "1: " + ' '.join(puppeteer_actions)
            self._conversation.append(puppeteer_text)

        print(self._puppeteer.log)

def print_args(args):
    print("agenda_path: {}".format(args.agenda_dir))
    print("agendas: {}".format(str(args.agenda_names)))
    print("nli_data_path: {}".format(args.nli_data_dir))
    print("nlu_data_path: {}".format(args.nlu_data_dir))

def demo(args):
    print_args(args)
    agenda_path = args.agenda_dir
    agenda_names = args.agenda_names
    nli_data_dir = args.nli_data_dir
    nlu_data_dir = args.nlu_data_dir
    
    # Set up trigger detector loader
    trigger_detector_loader = MyTriggerDetectorLoader(\
            nli_data_dir, nlu_data_dir, agenda_names)

    # Load agendas
    agendas = []
    for a in agenda_names:
        yml = "{}.yaml".format(a)
        path = os.path.join(agenda_path, yml)
        agenda = Agenda.load(path, trigger_detector_loader)
        print(str(agenda))
        agendas.append(agenda)
    
    tc = TestConversation(agendas)

    print('Type \'exit\' to terminate')
    while True:
        txt = input('text: ')
        if txt == 'exit':
            break

        tc.say(txt)

    print("-"*60)
    print("ACTIONS")
    print(tc._actions)
    print("-"*60)
    print("EXTRACTIONS")
    print(tc._extractions)
    print("-"*60)
    print("DIALOGUE")
    for line in tc._conversation:
        print(line)
    print("-"*60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Puppeteer demo")
    parser.add_argument("--agenda_dir", type=str, help='path to agenda directory')
    parser.add_argument("--agenda_names", nargs='+', type=str, help='list of agenda names')
    parser.add_argument("--nli_data_dir", type=str, help='path to NLI training data directory')
    parser.add_argument("--nlu_data_dir", type=str, help='path to NLU training data directory')
    args = parser.parse_args()
    args.agenda_dir = AGENDA_DIR
    args.agenda_names = AGENDA_NAMES
    args.nli_data_dir = NLI_DATA_DIR
    args.nlu_data_dir = NLU_DATA_DIR

    demo(args)
