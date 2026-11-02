#!/bin/bash
# usage: render.sh deck.pptx outdir
set -e
D=$(cd $(dirname $1); pwd)/$(basename $1); O=$2; mkdir -p $O/tmp; rm -f $O/s-*.png
cat > $O/p.xml <<X
<?xml version="1.0" encoding="utf-8"?>
<TaskQueueDataConvert><m_sFileFrom>$D</m_sFileFrom><m_sFileTo>$O/deck.pdf</m_sFileTo><m_nFormatTo>513</m_nFormatTo><m_sFontDir>/usr/share/fonts</m_sFontDir><m_sAllFontsPath>/home/khoale/.local/share/onlyoffice/desktopeditors/data/fonts/AllFonts.js</m_sAllFontsPath><m_sTempDir>$O/tmp</m_sTempDir></TaskQueueDataConvert>
X
(cd /opt/onlyoffice/desktopeditors/converter && ./x2t $O/p.xml >/dev/null 2>&1)
pdftoppm -png -r 110 $O/deck.pdf $O/s
ls $O/s-*.png | wc -l
