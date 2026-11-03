#!/bin/bash
set -e
B=$(dirname $(readlink -f $0))
export NM=/home/khoale/Documents/University/Semester_5/CE436_Discrete-Time_Signal_Processing/fpga-temp-predictor/docs/presentation/final_defense/.build/node_modules
export NODE_PATH=$NM SKILL=/home/khoale/.config/Claude/local-agent-mode-sessions/skills-plugin/52c68169-87b0-445d-8f1d-1ff1886c8139/de246fb9-091f-4a9a-9deb-2a4d86d1cc07/skills/pptx
cd $B; node deck.js $B/deck.pptx
python3 $SKILL/scripts/office/validate.py deck.pptx | tail -5
./render.sh deck.pptx $B/r
