from flask import Flask, render_template, request
from noir_search_engine import NoirSearchEngine
import logging

# Matikan log werkzeug agar terminal tidak berisik
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
engine = NoirSearchEngine()

@app.route("/")
def index():
    query = request.args.get("q", "").strip()
    results = []
    
    if query:
        # Panggil mesin pencari internal
        raw_results = engine.search(query, limit=20)
        
        # Konversi object hasil agar aman dikirim ke template
        for r in raw_results:
            # Reformat teks match agar memiliki style highlight di CSS HTML
            snippet = r['snippet'].replace('<b class="match term0">', '<span class="match">')\
                                  .replace('<b class="match term1">', '<span class="match">')\
                                  .replace('<b class="match term2">', '<span class="match">')\
                                  .replace('</b>', '</span>')
            
            results.append({
                "title": r['title'],
                "url": r['url'],
                "snippet": snippet
            })
            
    return render_template("index.html", query=query, results=results)

if __name__ == "__main__":
    print("\n" + "="*50)
    print(" NOIR SEARCH ENGINE WEB DASHBOARD AKTIF ")
    print(" Akses melalui browser Anda di: http://127.0.0.1:5000")
    print("="*50 + "\n")
    # Jalankan server
    app.run(host="127.0.0.1", port=5000, debug=False)
