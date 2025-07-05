from flask import Flask, session, redirect, url_for, render_template
from board import Board
from flask import jsonify, request

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # セッション管理に使用

# 難易度設定（9×9, 地雷10）
ROWS, COLS, MINES = 9, 9, 10

def get_board() -> Board:
    """セッションから Board オブジェクトを復元 or 新規作成"""
    if 'board' in session:
        data = session['board']
        b = Board(data['rows'], data['cols'], data['total_mines'])
        b.__dict__.update(data)
        return b
    else:
        b = Board(ROWS, COLS, MINES)
        session['board'] = b.__dict__
        return b

def save_board(b: Board):
    """Boardオブジェクトをセッションに保存"""
    session['board'] = b.__dict__

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/board')
def show_board():
    b = get_board()
    save_board(b)
    return render_template('board.html', board=b)

@app.route('/reveal/<int:r>/<int:c>')
def reveal(r, c):
    b = get_board()
    b.reveal(r, c)
    save_board(b)
    return redirect(url_for('show_board'))

@app.route('/flag/<int:r>/<int:c>')
def flag(r, c):
    b = get_board()
    b.flag(r, c)
    save_board(b)
    return redirect(url_for('show_board'))

@app.route('/reset')
def reset():
    session.pop('board', None)
    return redirect(url_for('index'))  # 難易度選択画面に戻る

@app.route('/set_difficulty/<level>')
def set_difficulty(level):
    if level == 'easy':
        rows, cols, mines = 9, 9, 10
    elif level == 'medium':
        rows, cols, mines = 16, 16, 40
    elif level == 'hard':
        rows, cols, mines = 16, 30, 99
    else:
        return redirect(url_for('index'))  # 無効な難易度
    
    b = Board(rows, cols, mines)
    session['board'] = b.__dict__
    return redirect(url_for('show_board'))

from flask import jsonify, request

@app.route('/api/board')
def api_board():
    b = get_board()
    return jsonify({
        'grid': b.grid,
        'revealed': b.revealed,
        'flagged': b.flagged,
        'game_over': b.game_over,
        'victory': b.victory,
        'rows': b.rows,
        'cols': b.cols,
    })

@app.route('/api/reveal', methods=['POST'])
def api_reveal():
    data = request.get_json()
    r, c = data['r'], data['c']
    b = get_board()
    b.reveal(r, c)
    save_board(b)
    return jsonify({'status': 'ok', 'game_over': b.game_over, 'victory': b.victory})

@app.route('/api/flag', methods=['POST'])
def api_flag():
    data = request.get_json()
    r, c = data['r'], data['c']
    b = get_board()
    b.flag(r, c)
    save_board(b)
    return jsonify({'status': 'ok'})

@app.route('/api/reset', methods=['POST'])
def api_reset():
    data = request.get_json()
    level = data.get('level', 'easy')

    if level == 'easy':
        rows, cols, mines = 9, 9, 10
    elif level == 'medium':
        rows, cols, mines = 16, 16, 40
    elif level == 'hard':
        rows, cols, mines = 16, 30, 99
    else:
        return jsonify({'error': 'invalid difficulty'}), 400

    b = Board(rows, cols, mines)
    save_board(b)
    return jsonify({'status': 'reset', 'rows': rows, 'cols': cols, 'mines': mines})

if __name__ == '__main__':
    app.run(debug=True)