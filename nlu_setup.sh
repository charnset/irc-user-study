# snips-nlu install: https://snips-nlu.readthedocs.io/en/latest/installation.html 
# need to install rustup first: https://www.rust-lang.org/tools/install 
# need g++ 
if ! command -v g++ > /dev/null; then
  echo "Installing g++ ..."
  sudo apt install g++
fi
pip cache purge
pip install setuptools-rust
pip install snips-nlu
python -m snips_nlu download en
