import random
from typing import List, Tuple, Set

class Board:
    def __init__(self, rows: int, cols: int, mines: int):
        self.rows = rows
        self.cols = cols
        self.total_mines = mines
        self.mines_placed = False  # 最初のクリック後に地雷を配置
        self.grid = [[0]*cols for _ in range(rows)]  # 地雷カウント or '*' 地雷マップ
        self.revealed = [[False]*cols for _ in range(rows)]
        self.flagged = [[False]*cols for _ in range(rows)]
        self.game_over = False
        self.victory = False

    def place_mines(self, safe: Tuple[int,int]):
        """最初のクリック位置 safe を避けて地雷をランダム配置"""
        positions = [(r, c) for r in range(self.rows) for c in range(self.cols) if (r,c)!=safe]
        mines = random.sample(positions, self.total_mines)
        for (r,c) in mines:
            self.grid[r][c] = '*'
        self._calculate_adjacent_counts()
        self.mines_placed = True

    def _calculate_adjacent_counts(self):
        """地雷の周囲セルに隣接地雷数を設定"""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == '*': continue
                cnt = 0
                for dr in (-1,0,1):
                    for dc in (-1,0,1):
                        rr, cc = r+dr, c+dc
                        if 0 <= rr < self.rows and 0 <= cc < self.cols and self.grid[rr][cc] == '*':
                            cnt += 1
                self.grid[r][c] = cnt

    def reveal(self, r: int, c: int):
        """セル(r,c)を開く処理。地雷ならゲームオーバー、0ならcascade"""
        if self.game_over or self.flagged[r][c] or self.revealed[r][c]:
            return
        if not self.mines_placed:
            self.place_mines((r, c))
        if self.grid[r][c] == '*':
            self.game_over = True
            self.revealed[r][c] = True
            return
        # 安全セルを開く
        self._flood_fill(r, c)
        self._check_victory()

    def _flood_fill(self, r: int, c: int):
        """DFSまたはBFSで0セルから自動展開（cascade）"""
        stack = [(r,c)]
        visited: Set[Tuple[int,int]] = set()
        while stack:
            x,y = stack.pop()
            if (x,y) in visited: continue
            visited.add((x,y))
            self.revealed[x][y] = True
            if self.grid[x][y] == 0:
                for dr in (-1,0,1):
                    for dc in (-1,0,1):
                        nx, ny = x+dr, y+dc
                        if 0 <= nx < self.rows and 0 <= ny < self.cols \
                           and (nx,ny) not in visited \
                           and not self.flagged[nx][ny]:
                            stack.append((nx, ny))
        # この方式はLeetCode 529 の DFS/BFS cascade と同じ仕組み :contentReference[oaicite:1]{index=1}

    def flag(self, r: int, c: int):
        """セルに旗を立てる／外す"""
        if self.game_over or self.revealed[r][c]:
            return
        self.flagged[r][c] = not self.flagged[r][c]

    def _check_victory(self):
        """非地雷セルが全て開いていれば勝ち"""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] != '*' and not self.revealed[r][c]:
                    return
        self.victory = True
        self.game_over = True