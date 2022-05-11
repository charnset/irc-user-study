pip cache purge
pip install -U scikit-learn
pip install -r requirements.txt
pip install snips-nlu
python -m snips_nlu download en
pip install spacy
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_lg
