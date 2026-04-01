\# Torah Data Download Protocol



\## Source



Sefaria API  

Version: Tanach\_with\_Ta'amei\_Hamikra  



URL template:

https://www.sefaria.org/api/texts/{book}?lang=he\&vhe=Tanach\_with\_Ta'amei\_Hamikra\&context=0\&pad=0\&commentary=0



\---



\## Books



\- Genesis  

\- Exodus  

\- Leviticus  

\- Numbers  

\- Deuteronomy  



\---



\## Procedure



1\. Query Sefaria API for each book  

2\. Extract Hebrew text from `he` field  

3\. Flatten nested structure into linear sequence  

4\. Join segments using newline separator  

5\. Save as UTF-8 plain text  



\---



\## Output



Location:

data/data\_raw/torah/



Files:

\- genesis\_raw.txt

\- exodus\_raw.txt

\- ...



\---



\## Metadata



For each file:

\- SHA256 hash

\- download date



Stored in:

metadata.json



\---



\## Notes



\- Text includes niqqud and ta'amim  

\- No normalization applied  

\- No filtering performed  

