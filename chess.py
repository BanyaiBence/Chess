class Board:
    def __init__(self) -> None:
        self._board: list[list[int]] = [[None for _ in range(8)] for _ in range(8)]
        self._available_for_castling: str = '-'
        self._en_passant: str = '-'
        self._turn: str = 'w'
        self.history: list[list] = []
        self._move_count: int = 0
        self._half__move_count: int = 0
        self.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    def __repr__(self) -> str:
        result = ''
        for i in range(8):
            for j in range(8):
                if self._board[j][i] is None:
                    result += '0 '
                else:
                    result += self._board[j][i] + ' '
            result += '\n'
        return result   
    @property
    def pieces(self) -> list[dict[str, list[int]]]:
        return [{"sticker": self._board[j][i], "pos": [j, i]} for i in range(8) for j in range(8) if self._board[j][i]]
    @pieces.setter
    def pieces(self):
        raise ValueError('Cannot set pieces')
    @property
    def half_move_count(self) -> int:
        return self._half__move_count
    @half_move_count.setter
    def half_move_count(self):
        raise ValueError('Cannot set half_move_count')
    @property
    def move_count(self) -> int:
        return self._move_count
    @move_count.setter
    def move_count(self):
        raise ValueError('Cannot set move_count')
    @property
    def fen(self) -> str:
        result: str = ''
        for i in range(8):
            empty_count: int = 0
            for j in range(8):
                if self._board[j][i] is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        result += str(empty_count)
                        empty_count = 0
                    result += self._board[j, i]
            if empty_count > 0:
                result += str(empty_count)
            result += '/'
        result = result[:-1]
        result += ' ' + self._turn +  + ' ' + self._available_for_castling + ' ' + self._en_passant + ' ' + str(self._half_move_count) + ' ' + str(self._move_count)
        return result
    @fen.setter
    def fen(self, value):
        self._board = [[None for _ in range(8)] for _ in range(8)]
        values = value.split(' ')
        rows = values[0].split('/')
        for i, row in enumerate(rows):
            j = 0
            for char in row:
                if char.isdigit():
                    j += int(char)
                else:
                    self._board[j][i] = char
                    j += 1
        self._turn = values[1]
        self._available_for_castling = values[2]
        self._en_passant = values[3]
        self.history = []
    @property
    def castles(self):
        return self._available_for_castling
    @castles.setter
    def castles(self):
        raise ValueError('Cannot set castles')
    @property
    def turn(self):
        return self._turn
    @turn.setter
    def turn(self):
        raise ValueError('Cannot set turn')
    @property
    def white_pieces(self):
        return [piece for piece in self.pieces if piece['sticker'].isupper()]
    @white_pieces.setter
    def white_pieces(self):
        raise ValueError('Cannot set white_pieces')
    @property
    def black_pieces(self):
        return [piece for piece in self.pieces if piece['sticker'].islower()]
    def validate_move(self, piece_sticker: str, piece_pos: list | tuple, pos: list | tuple, ignore_king_safety: bool = False) -> bool:
        if self._board[pos[0]][pos[1]] and piece_sticker.islower() == self._board[pos[0]][pos[1]].islower():
            return False
        if pos[0] < 0 or pos[0] > 7 or pos[1] < 0 or pos[1] > 7:
            return False
        if not ignore_king_safety and not self.is_safe_for_king(piece_sticker, piece_pos, pos):
            return False
        diff: list = [pos[0] - piece_pos[0], pos[1] - piece_pos[1]]
        # Normalize diff
        normal_diff: list = [1 if diff[0] > 0 else -1 if diff[0] < 0 else 0, 1 if diff[1] > 0 else -1 if diff[1] < 0 else 0]
        if diff == [0, 0]:
            return False
        if piece_sticker.lower() == 'p':
            if self._board[pos[0]][pos[1]]: # Capture
                if piece_sticker.isupper(): # White
                    return pos == [piece_pos[0] + 1, piece_pos[1] + 1] or pos == [piece_pos[0] - 1, piece_pos[1] + 1]
                else: # Black
                    return pos == [piece_pos[0] + 1, piece_pos[1] - 1] or pos == [piece_pos[0] - 1, piece_pos[1] - 1]
            # En passant
            if self._en_passant != '-':
                en_passant_pos = [ord(self._en_passant[0]) - 65, int(self._en_passant[1])]
                if piece_sticker.isupper():
                    return pos == [en_passant_pos[0], en_passant_pos[1] - 1] and (piece_pos[0] == en_passant_pos[0] + 1 or piece_pos[0] == en_passant_pos[0] - 1)
                else:
                    return pos == [en_passant_pos[0], en_passant_pos[1] + 1] and (piece_pos[0] == en_passant_pos[0] + 1 or piece_pos[0] == en_passant_pos[0] - 1)
            # Move
            if piece_sticker.isupper(): # White
                if piece_pos[1] == 6:
                    return pos == [piece_pos[0], piece_pos[1] - 1] or pos == [piece_pos[0], piece_pos[1] - 2]
                return pos == [piece_pos[0], piece_pos[1] - 1]
            else: # Black
                if piece_pos[1] == 1:
                    return pos == [piece_pos[0], piece_pos[1] + 1] or pos == [piece_pos[0], piece_pos[1] + 2]
                return pos == [piece_pos[0], piece_pos[1] + 1]
        if piece_sticker.lower() in 'rqb':
            if abs(normal_diff[0]) != abs(normal_diff[1]) and piece_sticker.lower() == 'b':
                return False
            if abs(normal_diff[0]) == abs(normal_diff[1]) and piece_sticker.lower() == 'r':
                return False
            current_pos = [piece_pos[0], piece_pos[1]] + normal_diff
            while current_pos != pos:
                if current_pos[0] < 0 or current_pos[0] > 7 or current_pos[1] < 0 or current_pos[1] > 7:
                    return False
                if self._board[current_pos[0]][current_pos[1]]:
                    if piece_sticker.islower() == self._board[current_pos[0]][current_pos[1]].islower():
                        return False
                current_pos += normal_diff
        if piece_sticker.lower() == 'n':
            knight_offsets = [[1, 2], [2, 1], [-1, 2], [-2, 1], [1, -2], [2, -1], [-1, -2], [-2, -1]]
            if diff not in knight_offsets:
                return False
            return True
        if piece_sticker.lower() == 'k':
            king_offsets = [[1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1]]
            if diff not in king_offsets:
                return False
            return True
        return False
    def is_safe_for_king(self, piece_sticker: str, piece_pos: list | tuple, pos: list | tuple) -> bool:
        taken_piece = self._board[pos[0]][pos[1]]
        self._board[pos[0]][pos[1]] = piece_sticker
        self._board[piece_pos[0]][piece_pos[1]] = None
        color = 'w' if piece_sticker.isupper() else 'b'
        result = not self.king_in_check(color)
        self._board[pos[0]][pos[1]] = taken_piece
        self._board[piece_pos[0]][piece_pos[1]] = piece_sticker
        return result
    def king_in_check(self, color: str) -> bool:
        king_pos: list = []
        for piece in self.pieces:
            piece_color: str = 'w' if piece['sticker'].isupper() else 'b'
            if piece['sticker'].lower() == 'k' and piece_color == color:
                king_pos = piece['pos']
                break
        for piece in self.pieces:
            piece_color = 'w' if piece['sticker'].isupper() else 'b'
            if piece_color == color:
                continue
            if self.validate_move(piece['sticker'], piece['pos'], king_pos, True):
                return True
        return False
    def all_moves(self, piece_sticker: str, piece_pos: list|tuple) -> list[list[int]]:
        result: list[list[int]] = []
        for i in range(8):
            for j in range(8):
                if self.validate_move(piece_sticker, piece_pos, [i, j]):
                    result.append([i, j])
        return result
    def castle(self, side: str) -> bool:
        if self._turn == 'w':
            if side == 'k':
                if 'K' not in self._available_for_castling:
                    return False
                if self._board[5][0] or self._board[6][0]:
                    return False
                if not self.is_safe_for_king('w', [4, 0]) or not self.is_safe_for_king('w', [5, 0]) or not self.is_safe_for_king('w', [6, 0]):
                    return False
                self._board[5][0] = 'R'
                self._board[6][0] = 'K'
                self._board[4][0] = None
                self._board[7][0] = None
                self._turn = 'b'
                self._move_count += 1
                self._half__move_count += 1
                self.history.append(['K', [4, 0], [6, 0], None])
                return True
            if side == 'q':
                if 'Q' not in self._available_for_castling:
                    return False
                if self._board[1][0] or self._board[2][0] or self._board[3][0]:
                    return False
                if not self.is_safe_for_king('w', [4, 0]) or not self.is_safe_for_king('w', [3, 0]) or not self.is_safe_for_king('w', [2, 0]):
                    return False
                self._board[3][0] = 'R'
                self._board[2][0] = 'K'
                self._board[4][0] = None
                self._board[0][0] = None
                self._turn = 'b'
                self._move_count += 1
                self._half__move_count += 1
                self.history.append(['K', [4, 0], [2, 0], None])
                return True
        if self._turn == 'b':
            if side == 'k':
                if 'k' not in self._available_for_castling:
                    return False
                if self._board[5][7] or self._board[6][7]:
                    return False
                if not self.is_safe_for_king('b', [4, 7]) or not self.is_safe_for_king('b', [5, 7]) or not self.is_safe_for_king('b', [6, 7]):
                    return False
                self._board[5][7] = 'r'
                self._board[6][7] = 'k'
                self._board[4][7] = None
                self._board[7][7] = None
                self._turn = 'w'
                self._move_count += 1
                self._half__move_count += 1
                self.history.append(['k', [4, 7], [6, 7], None])
                return True
            if side == 'q':
                if 'q' not in self._available_for_castling:
                    return False
                if self._board[1][7] or self._board[2][7] or self._board[3][7]:
                    return False
                if not self.is_safe_for_king('b', [4, 7]) or not self.is_safe_for_king('b', [3, 7]) or not self.is_safe_for_king('b', [2, 7]):
                    return False
                self._board[3][7] = 'r'
                self._board[2][7] = 'k'
                self._board[4][7] = None
                self._board[0][7] = None
                self._turn = 'w'
                self._move_count += 1
                self._half__move_count += 1
                self.history.append(['k', [4, 7], [2, 7], None])
                return True
        return False
    def move(self, piece_sticker: str, piece_pos: list|tuple, pos: list | tuple) -> bool:
        if self.validate_move(piece_sticker, piece_pos, pos):
            self._en_passant = '-'
            taken_piece = self._board[pos[0]][pos[1]]
            self._board[pos[0]][pos[1]] = piece_sticker
            self._board[piece_pos[0]][piece_pos[1]] = None
            if piece_sticker.lower() == 'p' and abs(piece_pos[1] - pos[1]) == 2:
                self._en_passant = self.pos_to_note([pos[0], pos[1] + 1])
            self._turn = 'b' if self._turn == 'w' else 'w'
            if self._turn == 'w':
                self._move_count += 1
            self._half__move_count += 1
            self.history.append([piece_sticker, piece_pos, pos, taken_piece])
            return True
        return False
    def reverse_last_move(self) -> bool:
        if not self.history:
            return False
        last_move: list = self.history.pop()
        self._board[last_move[1][0]][last_move[1][1]] = last_move[0]
        self._board[last_move[2][0]][last_move[2][1]] = last_move[3]
        self._turn = 'w' if self._turn == 'b' else 'b'
        if self._turn == 'b':
            self._move_count -= 1
        self._half__move_count -= 1
        return True
    def pos_to_note(self, pos: list | tuple) -> str:
        return chr(pos[0] + 65) + str(8 - pos[1])
