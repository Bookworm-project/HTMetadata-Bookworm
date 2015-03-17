


all: catalogworm


# The latest date can be hand-specified here.
latestDate=20150301
latestHathi=hathi_full_$(latestDate).txt.gz

$(latestHathi):
	curl -Lo $@ http://www.hathitrust.org/sites/www.hathitrust.org/files/hathifiles/$(latestHathi)


realjsoncatalog.txt: $(latestHathi)
	cat $(latestHathi) | gunzip -c | parallel --pipe -n10000 -j10 python3 generator.py > realjsoncatalog.txt


#I'm not putting a dependency on `realjsoncatalog.txt` so this doesn't continually rebuild
jsoncatalog.txt:
	mv realjsoncatalog.txt jsoncatalog.txt


# For the time being, just faking the input.txt on the basis of 
input.txt: jsoncatalog.txt
	cat $< | parallel --pipe -n1000 -P4 python3 fakeInput.py > $@

catalogworm: input.txt
	git clone git@github.com:Bookworm-Project/BookwormDB catalogworm
	cd catalogworm; make;




