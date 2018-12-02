from tinydb import TinyDB, where
from tinydb.operations import set

startingElo = 1000
weightingFactor = 32
placementMatches = 5

db = TinyDB('database')
users = db.table('users')
matches = db.table('matches')


def addUser(uID):
    uID = str(uID)
    if len(users.search(where('uID') == uID)) != 0:
        return False
    else:
        users.insert({'uID': uID, 'elo': startingElo})
        return True


def getUserElo(uID):
    uID = str(uID)
    count = users.count(where('uID') == uID)
    if users.count(where('uID') == uID) < 1:
        addUser(uID)
    userelo = users.get(where('uID') == uID)['elo']
    return userelo


def setUserElo(uID, newElo):
    uID = str(uID)
    newElo = int(newElo)
    users.update(set('elo', newElo), where('uID') == uID)


def getMatchCount(uID):
    uID = str(uID)
    return matches.count(where('p1') == uID) + matches.count(where('p2') == uID)


def addMatch(p1, p2, p1win):
    p1 = str(p1)
    p2 = str(p2)
    if len(users.search(where('uID') == p1)) != 1:
        return
    elif len(users.search(where('uID') == p2)) != 1:
        return
    else:
        matches.insert({'p1': p1, 'p2': p2, 'p1win': p1win})


def getWinProb (p1, p2):
    p1 = str(p1)
    p2 = str(p2)
    if (users.count(where('uID').matches(p1)) != 1) | (users.count(where('uID').matches(p2)) != 1):
        print('Something went wrong! Check database!')
        return
    p1elo = getUserElo(p1)
    p2elo = getUserElo(p2)
    prob = 1/(1+(10**((p2elo - p1elo)/400)))
    return prob


def computeGame(p1, p2, p1win):
    p1elo = getUserElo(p1)
    p2elo = getUserElo(p2)
    p1prob = getWinProb(p1, p2)
    p2prob = 1 - p1prob
    p1matchcount = getMatchCount(p1)
    p2matchcount = getMatchCount(p2)
    if p1win:
        p1elochange = weightingFactor * (1 - p1prob)
        p2elochange = weightingFactor * (0 - p2prob)
    else:
        p1elochange = weightingFactor * (0 - p1prob)
        p2elochange = weightingFactor * (1 - p2prob)
    if p1matchcount < placementMatches:
        p1multiplier = placementMatches - p1matchcount
    else:
        p1multiplier = 1
    if p2matchcount < placementMatches:
        p2multiplier = placementMatches - p2matchcount
    else:
        p2multiplier = 1
    setUserElo(p1, round(p1elo + p1multiplier * p1elochange))
    setUserElo(p2, round(p2elo + p2multiplier * p2elochange))
    addMatch(p1, p2, p1win)

