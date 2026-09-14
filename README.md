
![ChatGPT to LaTeX](https://github.com/quantasci/chat2pdf/blob/main/img_chat2pdf_thin.png)

# chat2pdf
2026 (c) Quanta Sciences | Rama Hoetzlein
MIT License

This tool converts ChatGPT Exported Backups to LaTeX / PDF.

## Requirements & Install
1. Install Python
2. Install a LaTeX distribution which has pdflatex.
3. Modify your environment path to include the latex binaries. e.g. On Windows you need to confirm that 'pdflatex' runs from the command prompt.
4. Clone this repository locally

## Usage
Steps to use:
1. Create an Export of your ChatGPT history. 
Goto your Profile -> Settings -> Data Controls -> Export data
You may needs to wait several days to receive the Export by e-mail.
2. Download & unzip the Export archive.
3. ChatGPT provides the archive as a folder of .json files. Confirm you have json files.
4. Run chat2pdf
The first argument is the path to the input archive folder containing .json files.
The second argument is the output folder for tex/pdf files.
```
python chat2pdf JsonFolder Chats
```
5. Output will include both .tex and .pdf files

## Results
Chat2pdf was tested on 731 chats, including many with math equations.
It was able to successfully convert 63% (463 files) chats on the first try.
For the remaining it provides a converted .tex file for further editing.

## Issues
This is a work-in-progress. Chat2pdf can fail to convert .tex to .pdf. 
In that case, it will print "Failed", and at least try to provide you with the .tex file.
You can then use your favorite editor (eg. Texmaker), run the .tex, and view the LaTeX errors yourself.
Often the errors are easily repaired to get a final pdf.






