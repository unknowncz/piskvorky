import threading, queue


depth = 9
winningnum = 3

def getinputs():
    x = int(input('move row(from top left): '))-1
    y = int(input('move column(from top left): '))-1
    return [x, y]


class game:
    def __init__(self, boardsize:int, eng=False) -> None:
        # static variable setup
        self.eng = eng
        self.checkingsequences = [''.join([str(j) for j in range(i, i+winningnum)]) for i in range(boardsize-winningnum+1)]
        self.ended = False
        self.boardsize = boardsize
        # dynamic variable setup
        self.diagonals = []
        self.antidiagonals = []

        self.board = (boardsize**2)*[1]

        self.rows = [self.board[i:i+self.boardsize] for i in range(0, len(self.board), self.boardsize)]

        for i in range(self.boardsize*2):
            t = []
            u = []
            for g in range(i):
                try:
                    t += [self.rows[i-g-1][g]]
                    u += [self.rows[g][i-g-1]]
                except IndexError:
                    pass
            if len(t):
                self.diagonals += [t]
            if len(u):
                self.antidiagonals += [u]

        self.moves = {k:v for k, v in enumerate(self.board)}
        self.playedmoves = {}

        if not eng:
            self.pprint()

    def play(self, pos, player):
        # check if move has been used
        if not self.board[pos[0]+pos[1]*self.boardsize] == 1:
            if not self.eng:
                print('invalid input')
            return False
        # update dynamic variables
        self.board[pos[0]+pos[1]*self.boardsize] = player+1

        self.moves.pop(pos[0]+pos[1]*self.boardsize)
        self.playedmoves |= {self.boardsize**2-len(self.moves):pos}

        self.rows[pos[0]][pos[1]] = player+1

        self.diagonals[pos[0] + pos[1]][pos[1] % len(self.diagonals[pos[0] + pos[1]])] = player+1 # this works now
        self.antidiagonals[pos[0] + self.boardsize - pos[1] - 1][pos[0] % len(self.antidiagonals[pos[0] + self.boardsize - pos[1] - 1])] = player+1 # TODO: remake this logic

        # check diag, row, col, antidiag for winningnum occurences in a row
        x = False
        # rowcheck and columncheck
        for i, r in enumerate(self.rows):
            x = self.checkforwin(r, player+1) or x
            x = self.checkforwin(list(zip(*self.rows[::-1]))[i], player+1) or x
        # diagcheck
        for d in self.diagonals:
            x = self.checkforwin(d, player+1) or x
        for d in self.antidiagonals:
            x = self.checkforwin(d, player+1) or x

        self.pprint()

        if x:
            self.ended = True
            self.winner = player
            return True

        # check for draw
        if not 1 in self.board:
            self.ended = True
            self.winner = 'Draw'

        return True

    def checkforwin(self, arr:list[int], player:int) -> bool:
        s = ''.join([str(i) for i, j in enumerate(arr) if j == player])
        return any((sublist in s) for sublist in self.checkingsequences)

    def evalposwrapper(self, startdepth=0, minormax=False, testgame=None, v=None):
        self.q.put({list(testgame.evalpos(startdepth+1, not minormax).keys())[0]:v}, block=True)

    def evalpos(self, startdepth=0, minormax=False) -> dict:
        # Not yet functional?
        self.eval = 0
        if startdepth > depth:
            # print(f'Depth {startdepth} reached.')
            return {0:tuple()}
        t = {}
        thl:list[threading.Thread]=[]
        self.q = queue.Queue()
        for k, v in self.moves.items():
            self.testgame = game(self.boardsize, True)
            self.testgame.pprint = self.passfunc
            for i, j in self.playedmoves.items():
                self.testgame.play(j, 2 if i%2 else 1)
                lastplayer = 2 if i%2 else 1
            self.testgame.play([v%self.boardsize, v//self.boardsize], lastplayer)
            if self.testgame.ended:
                invdepth = depth - startdepth - 1
                return {(invdepth if minormax else -invdepth):v}
            th = threading.Thread(target=self.evalposwrapper, args=(startdepth+1, not minormax, self.testgame, v))
            th.run()
            thl+=[th]

        qlen=len(self.q.queue)
        while True:
            if qlen==len(self.moves.items()):
                break

        # TODO: fix return value
        while True:
            if self.q.empty():
                break
            t|=self.q.get()
        self.eval = (min if minormax else max)(t.keys())
        if startdepth==0:
            return {self.eval:[t]}
        return {self.eval:t[self.eval]}

    def pprint(self):
        print()
        print(*self.rows, sep='\n')
        print()

    def passfunc(self):
        pass

if __name__ == '__main__':
    x = int(input('board size: '))
    g = game(x)
    p = 1
    while not g.ended:
        if g.play(getinputs(), p):
            p = 1 if p==2 else 2
            print(g.evalpos(minormax=p==1))
    print(f'winner: {g.winner}')
