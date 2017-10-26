import corpus_final as cf
from flask import Flask, request, render_template
app = Flask(__name__)
@app.route('/')
def index():
    if 'query' in request.args and request.args['query'] != '':
        c = cf.Corpus()
        c.open()
        if len(c.articles) == 0:
            return render_template('main.html', links=[], rebuilt='', deleted='')
        query = request.args['query']
        links = [(a, a.link) for a in c.request(query)][:10]
        return render_template('main.html', links=links)
    if 'del' in request.args and request.args['del'] == 'on':
        c = cf.Corpus()
        c.delete()
        return render_template('main.html', links=[], rebuilt = '', deleted = 'корпус удален')
    if 'vol' in request.args and request.args['vol'] != '':
        vol = int(request.args['vol'])
        c = cf.Corpus()
        c.delete()
        c.create(vol)
        c.lemmatize()
        c.clean()
        c = ''
        c = cf.Corpus()
        c.open()
        c.get_matrix()

        return render_template('main.html', links=[], rebuilt = 'корпус пересобран', deleted = '')

    return render_template('main.html', links=[], rebuilt = '', deleted = '')


if __name__ == '__main__':
    app.run(debug=True)

