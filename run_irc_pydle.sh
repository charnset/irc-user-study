export SERVER=10.101.110.39
export PORT=6697
export NUM_BOTS=3
export AGENDA_DIR=puppeteer-control

python3 irc_pydle.py \
    --server $SERVER \
    --port $PORT \
    --num_bots $NUM_BOTS \
    --agenda_dir $AGENDA_DIR \
    --agenda_names get_shipment get_payment get_website\
