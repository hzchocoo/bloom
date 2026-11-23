# Study Bloom

Study Bloom is a local Streamlit app that turns study notes into practice quizzes. Try the five-question DevOps sample or create a quiz from pasted notes or a PDF. The sample and PDF preview work without an API key. Drafts and attempts live in the current browser session.

## Run on Windows

Open the project in VS Code and run these commands in its PowerShell terminal. Use Python 3.11 or newer.

```powershell
Set-Location 'D:\Projects\study-bloom'
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:GEMINI_API_KEY = ([System.Net.NetworkCredential]::new('', (Read-Host 'Gemini API key' -AsSecureString))).Password
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address localhost --server.port 8501
```

Open [http://localhost:8501](http://localhost:8501) in your browser. Keep the terminal open while you use the app. Press **Ctrl+C** to stop it.

Skip the API key line to try the sample or preview notes. The key applies to the current PowerShell session and its child processes. If Streamlit is already running, stop it with **Ctrl+C** and run the launch command again after setting the key.

**Generate Quiz** sends the editable preview and quiz options to Gemini 3.1 Flash-Lite, which Google lists on the Gemini Developer API free tier. Get a key from [Google AI Studio](https://aistudio.google.com/apikey). If generation reports a quota limit, check your project's [Gemini rate limits](https://ai.google.dev/gemini-api/docs/rate-limits).

The second command uses the Python 3.12 installation found on this PC. On another Windows PC with the Python launcher configured, use this command in its place.

```powershell
py -m venv .venv
```

## Try the retry flow

Answer exactly two questions incorrectly and submit. Check that the score is **3 / 5**, then select **Retry 2 Mistakes**. The retry starts at **Question 1 of 2** and contains exactly the two questions you missed.

## Try a generated quiz

1. Open **Create Quiz**, name it, and paste notes into **Notes preview**. Check that the defaults are **5**, **Mixed**, and **English**.
2. Switch to **Upload PDF**, choose a text-based PDF and a page range, then click **Extract Text**. Edit the imported text in the preview. For scanned pages, use the same preview to paste the notes.
3. Click **Generate Quiz**. Check the reported draft count, edit a question, and delete another if available. Click **Start Quiz**, submit an attempt, and expand a **Source quote** in the results.
