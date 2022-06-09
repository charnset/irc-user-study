import os

from puppeteer import Agenda, Puppeteer
from puppeteer.trigger_detectors.loader import MyTriggerDetectorLoader

# Set up trigger detector loader
def print_args(args):
    print("agenda_path: {}".format(args.p))
    print("agendas: {}".format(str(args.a)))
    print("training_data_path: {}".format(args.t))

def load_puppeteer(directory, agenda_names):
    agenda_dir = directory + "/agendas/"
    nli_data_dir = directory + "/nli_premises/"
    nlu_data_dir = directory + "/nlu_training_data/"
    trigger_detector_loader = MyTriggerDetectorLoader(nli_data_dir, nlu_data_dir, agenda_names)
    # Load agendas
    agendas = []
    for a in agenda_names:
        yml = "{}.yaml".format(a)
        #print(yml)
        path = os.path.join(agenda_dir, yml)
        #print(path)
        agenda = Agenda.load(path, trigger_detector_loader)
        #print(str(agenda))
        agendas.append(agenda)

    return Puppeteer(agendas, plot_state=False)

