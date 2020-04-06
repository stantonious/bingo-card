from flask import Flask, render_template, request, send_file, send_from_directory
import numpy as np
import pkg_resources
import random
import struct
import matplotlib.pyplot as plt

app = Flask(__name__)


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


def get_random(val, d, l, skinny=3):
    d_10, d_0 = divmod(val, 10)
    r = np.squeeze(d[np.argwhere(l == d_0), ...])
    idx = np.random.randint(0, r.shape[0])
    r_10 = np.squeeze(d[np.argwhere(l == d_10), ...])
    idx_10 = np.random.randint(0, r_10.shape[0])
    r = np.concatenate((r_10[idx_10, :, :-skinny], r[idx, :, skinny:]), axis=-1)

    # add border
    r[[0, -1], :] = 255
    r[:, [0, -1]] = 255

    return r


def get_column(minmax, num, d, l, skinny):
    r = []

    for _n in sorted(random.sample(range(minmax[0], minmax[1] + 1), k=num)):
        print(_n)
        r.append(get_random(_n, d, l, skinny))
    return np.asarray(r)


def to_png(d, cmap='RdPu'):
    from io import BytesIO
    outf = BytesIO()
    plt.imsave(outf, d, cmap=cmap, format='png')
    outf.seek(0)
    return outf


B = (1, 15)
I = (16, 30)
N = (31, 45)
G = (46, 60)
O = (61, 75)

colors = ['jet',
          'ocean',
          'inferno',
          'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
          'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
          'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']


@app.route("/get_img/<path:path>")
def get_img(path):
    print(path)
    return send_from_directory('data', path)


@app.route("/get_card")
def get_card():
    cmap = request.args.get('cmap', 'RdPu')
    vals = [
        sorted(random.sample(range(1, 15), k=5)),
        sorted(random.sample(range(16, 30), k=5)),
        sorted(random.sample(range(31, 45), k=5)),
        sorted(random.sample(range(45, 60), k=5)),
        sorted(random.sample(range(61, 75), k=5)),
    ]

    vals = np.asarray(vals)
    vals = vals.T

    return render_template('card.html', numbers=vals, cmap=cmap, colors=colors)


@app.route("/get_image")
def get_image():
    val = int(request.args.get('val'))
    cmap = request.args.get('cmap', 'RdPu')
    bits = get_random(val, d, l, skinny=4)
    return send_file(to_png(bits, cmap), mimetype='image/png')


@app.route("/")
def template_test():
    return render_template('template.html', my_string="Wheeeee!", my_list=[0, 1, 2, 3, 4, 5])


d = read_idx(pkg_resources.resource_filename(__name__, 'data/t10k-images-idx3-ubyte'))
l = read_idx(pkg_resources.resource_filename(__name__, 'data/t10k-labels-idx1-ubyte'))

if __name__ == '__main__':
    app.run(debug=True)
