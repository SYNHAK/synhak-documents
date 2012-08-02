# Used on synhak.org to publish files to http://synhak.org/~secretary/

cd /home/secretary/synhak-documents/latex
git pull
git checkout -f master
make
rsync -avz *.pdf --delete /home/secretary/public_html/docs/

cd /home/secretary/synhak-documents/svg
make
rsync -avz *.pdf *.png *.svg --delete /home/secretary/public_html/docs/images/

cd /home/secretary/synhak-bylaws/
git pull
git checkout -f master
make
cp *.pdf /home/secretary/public_html/docs/
