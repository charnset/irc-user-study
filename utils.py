import re
import spacy

nlp = spacy.load("en_core_web_sm")


def get_simple_sentences(msg):
    """Split a massage by punctuations ('.', ',', ':', ';')
    if the split sentence is compound (FANBOYS: For, And, Nor, But, Or, Yet, So)
    then segment it into multiple simple sentences
    a simple sentence is a sequence of word in which
    its dependency tree contains at least one VERB token and one SUBJ token (nsubj, csubj)
    """
    sentences = set()
    split_msg = re.split("[" + ".,:;" + "]+", msg)
    split_msg = [s.strip().lower() for s in split_msg if s.strip()]
    # print(split_msg)

    if len(split_msg) > 1:
        sentences.update(split_msg)

    for m in split_msg:
        text = nlp(m)
        conj_idx = []
        for token in text:
            if token.text in [
                "for",
                "and",
                "nor",
                "but",
                "or",
                "yet",
                "so",
            ]:  # CONJUNCTIONS: FANBOYS
                conj_idx.append(token.i)

        # print(conj_idx)

        clauses = []
        if conj_idx:
            span = text[: conj_idx[0]]
            cl = " ".join([t.text for t in span])
            clauses.append(cl)

        for j, idx in enumerate(conj_idx):
            start = conj_idx[j]
            end = conj_idx[j + 1] if j + 1 < len(conj_idx) else None
            span = text[start:end] if j + 1 < len(conj_idx) else text[start:]
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
                cl = " ".join([t.text for t in span[:]])
                clauses.append(cl)
            else:
                phrase = " " + " ".join([t.text for t in span])
                clauses[-1] += phrase

        clauses = [cl.strip() for cl in clauses if cl.strip()]
        # print(clauses)
        sentences.update(clauses)

    return list(sentences)


def get_agenda_state_log(agenda_name, at_state):
    """Log for each agenda,
    which state we are at,
    how much confidence we are at that state,
    how many consecutive turns we have been idle
    """
    return "{{agenda: {}, at_state: {}, prob: {:.3f}, been_idle: {}}}".format(
        agenda_name, at_state[0], at_state[1], at_state[2]
    )
