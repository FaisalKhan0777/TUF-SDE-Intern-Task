import requests

JUDGE0_URL = "https://judge0-ce.p.rapidapi.com"
JUDGE0_HEADERS = {
    "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
    "X-RapidAPI-Key": "YOUR_API_KEY"  # Replace with your RapidAPI key
}

@app.route('/submissions')
def submissions():
    snippets = cache.get('submissions')
    if snippets is None:
        snippets = CodeSnippet.query.all()
        for snippet in snippets:
            if not snippet.stdout:  # Check if stdout is not already fetched
                snippet.stdout = fetch_stdout_from_judge0(snippet.code, snippet.language)
                db.session.commit()
        cache.set('submissions', snippets, timeout=60)  # Cache for 60 seconds
    return render_template('submissions.html', snippets=snippets)

def fetch_stdout_from_judge0(code, language):
    endpoint = f"{JUDGE0_URL}/submissions?wait=true&base64_encoded=false&fields=stdout"
    payload = {
        "source_code": code,
        "language_id": language_to_id(language),
        "stdin": "",  # We don't need stdin for this case
        "expected_output": ""  # We don't have expected output for this case
    }
    response = requests.post(endpoint, json=payload, headers=JUDGE0_HEADERS)
    if response.status_code == 201:
        submission_id = response.json()["id"]
        submission_result = None
        while submission_result is None or submission_result['status']['id'] <= 2:  # Pending or In Queue
            response = requests.get(f"{JUDGE0_URL}/submissions/{submission_id}", headers=JUDGE0_HEADERS)
            submission_result = response.json()
        if submission_result['status']['id'] == 3:  # Accepted
            return submission_result['stdout']
        else:
            return "Error: Failed to execute code"
    else:
        return "Error: Failed to submit code"

def language_to_id(language):
    # Mapping of languages to Judge0 language IDs
    languages = {
        "C++": 54,
        "Java": 62,
        "JavaScript": 63,
        "Python": 71
    }
    return languages.get(language, 0)
