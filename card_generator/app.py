from flask import Flask, render_template, request, send_file, send_from_directory
import numpy as np
import pkg_resources
import random
import struct
import matplotlib.pyplot as plt

app = Flask(__name__)

IGNORE = [8, 31, 44, 45, 69]


def _generate_bingo_numbers(ignore=None):
    ignore = ignore or []
    B = [x for x in range(1, 16) if x not in ignore]
    I = [x for x in range(16, 31) if x not in ignore]
    N = [x for x in range(31, 46) if x not in ignore]
    G = [x for x in range(46, 61) if x not in ignore]
    O = [x for x in range(61, 76) if x not in ignore]

    return B, I, N, G, O


def read_idx(filename):
    # https://gist.github.com/tylerneylon/ce60e8a06e7506ac45788443f7269e40
    with open(filename, 'rb') as f:
        zero, data_type, dims = struct.unpack('>HBB', f.read(4))
        shape = tuple(struct.unpack('>I', f.read(4))[0] for d in range(dims))
        return np.fromstring(f.read(), dtype=np.uint8).reshape(shape)


def read_labels(filename):
    with open(filename, 'rb') as f:
        zero, num = struct.unpack('>ii', f.read(8))
        return np.fromstring(f.read(), dtype=np.uint8)


def get_random(val, d, l, idxs, skinny=3):
    d_10, d_0 = divmod(val, 10)
    r = ds[d_0][idxs[d_0], ...]
    r_10 = ds[d_10][idxs[d_10], ...]
    r = np.concatenate((r_10[:, :-skinny], r[:, skinny:]), axis=-1)

    # add border
    r[[0, -1], :] = 255
    r[:, [0, -1]] = 255

    return r


def to_png(d, cmap='RdPu'):
    from io import BytesIO
    outf = BytesIO()
    plt.imsave(outf, d, cmap=cmap, format='png')
    outf.seek(0)
    return outf


colors = [
    'YlGnBu',
    'jet',
    'ocean',
    'inferno',
    'Greys',
    'Purples',
    'Blues',
    'Greens',
    'Oranges',
    'Reds',
    'YlOrBr',
    'YlOrRd',
    'OrRd',
    'PuRd',
    'RdPu',
    'BuPu',
    'GnBu',
    'PuBu',
    'YlGnBu',
    'PuBuGn',
    'BuGn',
    'YlGn']


@app.route("/get_img/<path:path>")
def get_img(path):
    print(path)
    return send_from_directory('data', path)


def get_idxs():
    r = []

    for _n in range(10):
        r.append(np.random.randint(0, ds[_n].shape[0]))
    return r


def _decode_numbers2(numbers):
    import re
    n = re.sub(r'[\[\]]', '', numbers)
    n = re.sub(r'[ ]+', ' ', n)

    r = []
    for _n in n.strip().split(' '):
        r.append(int(_n))

    return np.asarray(r).reshape(5, 5, 2)


def _decode_numbers(numbers):
    r = []

    if not numbers:
        return None

    for _i, _n in enumerate(numbers[1:-1].split('\n')):
        _r = []
        for _ii, _nn in enumerate(_n.strip()[1:-1].split(' ')):
            try:
                _r.append(int(_nn))
            except:
                pass
        r.append(np.asarray(_r))
    return np.asarray(r, )


@app.route("/get_card_only", methods=['POST'])
def get_card_only():
    cmap = request.json.get('cmap', 'Oranges')
    numbers = request.json.get('numbers', None)
    idxs = [int(x) for x in request.json.get('idxs')[1:-1].split(',')]
    invert_number = request.json.get('invert_number', None)
    clear = request.json.get('clear', None)

    if not numbers:
        numbers = get_new_numbers()
    else:
        numbers = _decode_numbers2(numbers)
    if invert_number:
        invert_number = int(invert_number)
        s_idxs = np.argwhere(numbers[..., 0] == invert_number)[0]
        numbers[s_idxs[0], s_idxs[1], 1] *= -1

    if clear:
        state = np.full((5, 5), -1)
        numbers = numbers[..., 0]
        numbers = np.stack((numbers, state), -1)
    return render_template('card_only.html',
                           numbers=numbers,
                           idxs=idxs,
                           cmap=cmap,
                           )


def get_new_numbers(ignore=None):
    state = np.full((5, 5,), -1)

    B, I, N, G, O = _generate_bingo_numbers(ignore)

    vals = [
        random.sample(B, k=5),
        random.sample(I, k=5),
        random.sample(N, k=5),
        random.sample(G, k=5),
        random.sample(O, k=5),
    ]

    vals = np.asarray(vals)
    vals = vals.T

    vals[2, 2] = -1
    vals = np.stack((vals, state), axis=-1)

    return vals


@app.route("/", methods=['GET'])
@app.route("/get_card", methods=['GET'])
def get_card_get():
    cmap = request.args.get('cmap', 'Oranges')
    numbers = request.args.get('numbers', None)
    regen = request.args.get('regen', None)
    ignore = request.args.getlist('ignore', None)

    if ignore and len(ignore) == 1 and ',' in ignore[0]:
        ignore = ignore[0].split(',')

    if ignore:
        ignore = [int(_n) for _n in ignore]

    if numbers and not regen:
        vals = _decode_numbers2(numbers)
        idxs = [int(x) for x in request.json.get('idxs')[1:-1].split(',')]
    else:
        idxs = get_idxs()
        vals = get_new_numbers(ignore=ignore)

    return render_template('card.html',
                           numbers=vals,
                           idxs=idxs,
                           cmap=cmap,
                           colors=colors, )


@app.route("/get_card", methods=['POST'])
def get_card():
    if request.json:
        cmap = request.json.get('cmap', 'Oranges')
        numbers = request.json.get('numbers', None)
        regen = request.json.get('regen', None)
        ignore = request.json.get('ignore', None)
    else:
        cmap = 'Oranges'
        numbers = None
        regen = None
        ignore = None

    if numbers and not regen:
        vals = _decode_numbers2(numbers)
        idxs = [int(x) for x in request.json.get('idxs')[1:-1].split(',')]
    else:
        idxs = get_idxs()
        vals = get_new_numbers()

    return render_template('card.html',
                           numbers=vals,
                           idxs=idxs,
                           cmap=cmap,
                           colors=colors, )


@app.route("/get_image")
def get_image():
    val = int(request.args.get('val'))
    idxs = [int(x) for x in request.args.get('idxs')[1:-1].split(',')]
    invert = int(request.args.get('invert', -1))

    if val < 0:
        return send_from_directory('data', 'free.png')

    cmap = request.args.get('cmap', 'RdPu')

    if invert == 1:
        cmap += '_r'
        print('invert', cmap)
    bits = get_random(val, d, l, idxs=idxs, skinny=4)
    print('cmap', cmap)
    return send_file(to_png(bits, cmap), mimetype='image/png')


@app.route("/")
def template_test():
    return render_template('template.html', my_string="Wheeeee!", my_list=[0, 1, 2, 3, 4, 5])


d = read_idx(pkg_resources.resource_filename(__name__, 'data/t10k-images-idx3-ubyte'))
l = read_idx(pkg_resources.resource_filename(__name__, 'data/t10k-labels-idx1-ubyte'))
ds = dict()
ds[0] = np.squeeze(d[np.argwhere(l == 0), ...])
ds[1] = np.squeeze(d[np.argwhere(l == 1), ...])
ds[2] = np.squeeze(d[np.argwhere(l == 2), ...])
ds[3] = np.squeeze(d[np.argwhere(l == 3), ...])
ds[4] = np.squeeze(d[np.argwhere(l == 4), ...])
ds[5] = np.squeeze(d[np.argwhere(l == 5), ...])
ds[6] = np.squeeze(d[np.argwhere(l == 6), ...])
ds[7] = np.squeeze(d[np.argwhere(l == 7), ...])
ds[8] = np.squeeze(d[np.argwhere(l == 8), ...])
ds[9] = np.squeeze(d[np.argwhere(l == 9), ...])
d = None

if __name__ == '__main__':
    app.run(debug=True)
