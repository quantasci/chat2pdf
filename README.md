
![ChatGPT to LaTeX](https://github.com/quantasci/chat2pdf/blob/main/img_chat2pdf_thin.png)

# chat2pdf
2026 (c) Quanta Sciences | Rama Hoetzlein<br>
MIT License

This tool converts ChatGPT Exported Backups for json format to LaTeX / PDF.

## Requirements & Install
1. Install Python
2. Install a LaTeX distribution which has pdflatex.
3. Modify your environment path to include the latex binaries. e.g. On Windows you need to confirm that 'pdflatex' runs from the command prompt.
4. Clone this repository locally

## Usage
Steps to use:
1. Create an Export of your ChatGPT history. <br>
Goto your Profile -> Settings -> Data Controls -> Export data<br>
You may needs to wait several days to receive the Export by e-mail.<br>
2. Download & unzip the Export archive.
3. ChatGPT provides the archive as a folder of .json files. Confirm you have json files.
4. Run chat2pdf<br>
The first argument is the path to the input archive folder containing .json files.<br>
The second argument is the output folder for tex/pdf files.
```
python chat2pdf input_json_folder output_folder
```
5. Output will include both .tex and .pdf files

## Results
Chat2pdf was tested on 731 chats, including many with math equations.<br>
It was able to successfully convert 63% (463 files) chats on the first try.<br>
For the remaining it provides a converted .tex file for further editing.

## Issues & Limitations
This is a work-in-progress. Chat2pdf can fail to convert .tex to .pdf. 
In that case, it will print "Failed", and at least try to provide you with the .tex file.
You can then use your favorite editor (eg. Texmaker), run the .tex, and view the LaTeX errors yourself.
Often the errors are easily repaired to get a final pdf.
Chat2pdf does not handle images currently.

## Algorithm Details
Conversion from ChatGPT Backup to downloadable LaTeX/PDF would hopefully be a part of ChatGPT in the future.
Chat2pdf currently fills this role from the exported json archives provided by OpenAI/ChatGPT.
<br>
The following general strategy converts the json to LaTeX:
1. Chats are stored in a json node tree, with ChatGTP responses as children of User queries<br>
2. Sibling chats are organized by chronology via the create_time.<br>
3. For each conversation, chats are extracted by sorting chronologically and evaluating depth-first, to give the correct output ordering of messages.<br>
4. Messages are cleaned of ChatGTP content markers, and Genui (generative UI outputs), which don't translate easily to LaTeX.<br>
5. Unicode characters are converted to symbols, ascii, or whenever possible to math symbols. For example, math operations such as less-than-equal ≤, are converted to LaTeX $leq$. <br>
6. Markdown is converted to LaTeX. Common symbols (% & #) are converted to LaTeX escapes (\% \& \#). ChatGPT citation artifacts are removed. Existing math/LaTeX blocks in the chat are preserved whenever possible. Markdown headings (# ## ###) are converted to LaTeX \sections and \subsections. Bold and italic are converted to \textit{}, \textbf{}. <br>
7. User input sections are marked with a yellow box (\begin{userbox} via tcolorbox package), to more easily distinguish from ChatGPT responses. <br>
8. The header.tex is prepended to the .tex file to provide all the necessary packages.<br>
9. The final .tex file is run through pdf2latex to generate .pdf<br>
10. Output .tex and .pdf are given dated names, for easier sorting by original chat date. If the generation fails, it prints a message, but still keeps the .tex for further inspection.<br>

## Citation of this Work
2026. Hoetzlein, Rama. "chat2pdf: Conversion of ChatGPT chat history to LaTeX". Retrieved from: github.com/quantasci/chat2pdf











