from flask import Flask, jsonify, request
from libgen_api_enhanced import LibgenSearch
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/search_book', methods=['GET'])
def search_book():
    # Get the book title from the query parameters
    title = request.args.get('title')
    if not title:
        return jsonify({"error": "Title is required"}), 400

    s = LibgenSearch()
    results = s.search_default(title)

    books = []
    for result in results:
        mirror_1 = result.get('Mirror_1')
        if not mirror_1:
            continue

        page = requests.get(mirror_1)
        soup = BeautifulSoup(page.text, "html.parser")

        links = []
        res = soup.find_all("li")
        for i in res:
            a_tag = i.find("a")
            if a_tag and 'href' in a_tag.attrs:
                next_link = a_tag['href']
                links.append(next_link)

        img_tag = soup.find("img")
        img_link = img_tag['src'] if img_tag and 'src' in img_tag.attrs else None

        book = {
            'id': result.get('ID'),
            'title': result.get('Title'),
            'author': result.get('Author'),
            'year': result.get('Year'),
            'pages': result.get('Pages'),
            'lang': result.get('Language'),
            'extension': result.get('Extension'),
            'Cloudflare': links[0] if len(links) > 0 else None,
            'Ipfs': links[1] if len(links) > 1 else None,
            'Pinata': links[2] if len(links) > 2 else None,
            'image': f"https://library.lol{img_link}" if img_link else None
        }
        books.append(book)

    return jsonify(books)

if __name__ == '__main__':
    app.run(debug=True)
