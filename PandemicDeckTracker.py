# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 09:52:08 2020

@author: Andy Korinda
"""

import json
import math


def new_game(infection_deck, player_deck):
    for key, val in infection_deck['cities'].items():
        if val['city'] == 'Hollow Men':
            val['location'] = 'discard'
        elif (val['location'] != 'inoculated' and
              val['location'] != 'destroyed'):
            val['location'] = 'deck'

    city_count = 0
    for key, val in player_deck['cities'].items():
        if (val['location'] == 'deck' or
                val['location'] == 'discard'):
            city_count += 1
            val['location'] = 'deck'
    if city_count <= 36:
        ep_cards = 5
    elif city_count <= 44:
        ep_cards = 6
    elif city_count <= 51:
        ep_cards = 7
    elif city_count <= 57:
        ep_cards = 8
    elif city_count <= 62:
        ep_cards = 9
    else:
        ep_cards = 10

    print('Use ' + str(ep_cards) + ' epidemic card')
    player_deck['epidemic'] = ep_cards

    request_qty = True
    while request_qty:
        rationed_qty = input('How man rationed events do you get? ')
        try:
            player_deck['rationed'] = int(rationed_qty)
            request_qty = False
        except ValueError:
            pass

    card_cnt = city_count
    for key, val in player_deck.items():
        if key != 'cities':
            card_cnt += player_deck[key]
    cards_per_pile = math.floor(card_cnt / player_deck['epidemic'])
    cards_extra = card_cnt % player_deck['epidemic']

    pile = {}
    for ii in range(0, player_deck['epidemic']):
        if cards_extra > 0:
            extra = 1
            cards_extra -= 1
        else:
            extra = 0
        pile = {ii: {'qty': cards_per_pile + extra + 1, 'epidemic': True}}

    return infection_deck, player_deck, pile


def open_deck():
    with open('infection.json', 'r') as f:
        infection_deck = json.load(f)

    with open('player.json', 'r') as f:
        player_deck = json.load(f)

    with open('piles.json', 'r') as f:
        piles = json.load(f)

    return infection_deck, player_deck, piles


def save_deck(infection_deck, player_deck, piles):
    with open('infection.json', 'w') as f:
        json.dump(infection_deck, f)

    with open('player.json', 'w') as f:
        json.dump(player_deck, f)

    with open('piles.json', 'w') as f:
        json.dump(piles, f)

    return


def city_verb(city, verb, deck):
    city = city.title()

    found = False
    for key, val in deck['cities'].items():
        if (val['city'] == city and (
                val['location'] == 'deck' or
                val['location'] == 'top')):
            val['location'] = 'discard'
            found = True
            break

    if not found:
        print(city + ' was not found')

    return deck


def connect_city(city, infection_deck, player_deck):
    city = city.title()

    while True:
        city_qty = input('What is the cities population? ')
        try:
            city_qty = int(city_qty)
            break
        except ValueError:
            pass
    for ii in range(1, city_qty):
        try:
            infection_deck['cities'][str(int(max(infection_deck['cities'])) + 1)] = {'city': city,
                                                                                     'location': 'game end'}

        except ValueError:
            infection_deck['cities']['1'] = {'city': city, 'location': 'game end'}
            pass

        except TypeError:
            print('Fatal Error, none integer value used as city key')

        try:
            player_deck['cities'][str(int(max(player_deck['cities'])) + 1)] = {'city': city,
                                                                               'location': 'discard'}

        except ValueError:
            player_deck['cities']['1'] = {'city': city, 'location': 'discard'}
            pass

        except TypeError:
            print('Fatal Error, none integer value used as city key')

    return infection_deck, player_deck


def inoculate(city, deck):
    city = city.title()

    for key, val in deck['cities'].items():
        if val['city'] == city and val['location'] == 'discard':
            val['location'] = 'inoculated'
            break

    crd_cnt = 0

    for key, val in deck['cities'].items():
        if val['location'] == 'inoculated':
            crd_cnt += 1

    print(str(crd_cnt) + ' cards inoculated from this deck')
    return deck


def evaluate_decks(infection_deck, player_deck, piles):
    print('\n--Card Probabilities--')
    loc_cnts = {
        'top': 0,
        'deck': 0
    }
    for loc_key in loc_cnts:
        deck_cnt = {}
        for key, val in infection_deck['cities'].items():
            if val['location'] == loc_key:
                city = val['city']
                loc_cnts[loc_key] += 1
                try:
                    deck_cnt[city] += 1
                except KeyError:
                    deck_cnt.update({city: 1})
                    pass

        if loc_cnts[loc_key] > 0:
            # Sort in reverse order
            ord_cnt = {k: v for k, v in sorted(deck_cnt.items(),
                                               key=lambda item: item[1],
                                               reverse=True)}
            print(loc_key.title() + ' Cards')
            for ord_key, ord_val in ord_cnt.items():
                chance = round(ord_val / loc_cnts[loc_key] * 100)
                print(ord_key + ': ' + str(chance) + '%')

            print('-------------------')
        if loc_cnts[loc_key] > 5:
            break

    # TODO: calculate the probability of an epidemic
    loc_cnts.clear
    loc_cnts = {
        'deck': 0,
        'discard': 0
    }
    for key, val in player_deck['cities'].items():
        for loc_key in loc_cnts:
            if val['location'] == loc_key:
                city = val['city']
                loc_cnts[loc_key] += 1

    # TODO: display how many infection cards are inoculated
    # TODO: display how many player cards are inoculated
    # TODO: display the total size of the non-inoculated player deck


def epidemic(infection_deck):
    # Intensify
    intensify_city = input('Intensify city: ')
    infection_deck = city_verb(intensify_city, 'discard', infection_deck)

    # Shuffle
    for key, val in infection_deck['cities'].items():
        if val['location'] == 'discard':
            val['location'] = 'top'

    return infection_deck


cmd_list = [
    'new game',
    'new deck',
    'save deck',
    'open deck',
    'draw CARD',
    'infect CITY',
    'inoculate CITY',
    'connect CITY',
    'destroy CARD',
    'evaluate deck',
    'end game'
]

action_list = []
for x in range(0, (len(cmd_list))):
    action_list.append(cmd_list[x].split(' ', 1)[0])

infdeck = {
    'cities': {
        '1': {
            'city': 'New York',
            'location': 'deck'
        },
        '2': {
            'city': 'Chicago',
            'location': 'top'
        }
    }
}

pldeck = {
    'cities': {
        '1': {
            'city': 'New York',
            'location': 'deck'
        },
        '2': {
            'city': 'London',
            'location': 'discard'
        }
    },
    'epidemic': 0,
    'rationed': 0,
    'unrationed': 2,
    'produce supplies': 8,
    'antiviral lab': 3
}

print('-------------------\n' +
      'Welcome to Pandemic Legacy Season 2\n\tCard Tracker\n' +
      '-------------------\n')

while True:
    usr_cmd = input('[N]ew Game or [O]pen Deck: ')
    usr_cmd = usr_cmd.lower()

    if (usr_cmd == 'n' or
            usr_cmd == 'new game'):
        infdeck, pldeck, plpiles = new_game(infdeck, pldeck)
        print('Good Luck!')
        break
    elif (usr_cmd == 'o' or
          usr_cmd == 'open deck'):
        infdeck, pldeck, plpiles = open_deck()
        break
    else:
        print('Command not recognized. Please try again')

while True:
    evaluate_decks(infdeck, pldeck, plpiles)

    usr_cmd = input('Command: ')
    usr_cmd = usr_cmd.lower()
    usr_cmd = usr_cmd.strip()
    print('')

    action = usr_cmd.split(' ', 1)[0]

    try:
        noun = usr_cmd.split(' ', 1)[1]
    except IndexError:
        noun = ''
        pass

    if (action in action_list and
            noun != ''):
        if action == 'new':
            if noun == 'game':
                infdeck, pldeck, plpiles = new_game(infdeck, pldeck)
                print('Good Luck!')
            elif noun == 'deck':
                print('This command is still in development')
                infdeck = {
                    'cities': {}
                }

                pldeck = {
                    'cities': {},
                    'epidemic': 0,
                    'rationed': 0,
                    'unrationed': 0,
                    'produce supplies': 0,
                    'antiviral lab': 0
                }

                request_qty = True
                while request_qty:
                    qty = input('How many unrationed cards? ')
                    try:
                        pldeck['unrationed'] = int(qty)
                        request_qty = False
                    except ValueError:
                        print('Not an integer')
                        pass

                request_qty = True
                while request_qty:
                    qty = input('How many "Produce Supplies" cards? ')
                    try:
                        pldeck['produce supplies'] = int(qty)
                        request_qty = False
                    except ValueError:
                        print('Not an integer')
                        pass

                request_qty = True
                while request_qty:
                    qty = input('How many "Antiviral Lab"cards? ')
                    try:
                        pldeck['antiviral lab'] = int(qty)
                        request_qty = False
                    except ValueError:
                        print('Not an integer')
                        pass
            else:
                print('Unknown new NOUN')

        elif action == 'infect':
            infdeck = city_verb(noun, 'discard', infdeck)

        elif action == 'connect':
            infdeck, pldeck = connect_city(noun, infdeck, pldeck)

        elif action == 'inoculate':
            request_deck = True
            while request_deck:
                deck_type = input('Player or Infection deck? ')
                deck_type = deck_type.lower()
                deck_type = deck_type.strip()

                if deck_type == 'infection':
                    infdeck = inoculate(noun, infdeck)
                    request_deck = False

                elif deck_type == 'player':
                    pldeck = inoculate(noun, pldeck)
                    request_deck = False

                elif deck_type == 'end game':
                    print('Ending the game')
                    break

                else:
                    print('Did not recognize the deck')

        elif action == 'draw':
            if noun == 'epidemic':
                pldeck['epidemic'] -= 1
                epidemic(infdeck)
            elif (noun == 'rationed' or
                  noun == 'unrationed' or
                  noun == 'produce supplies' or
                  noun == 'antiviral lab'):
                pldeck[noun] -= 1
            else:  # assume it is a city
                pldeck = city_verb(noun, 'discard', pldeck)
                plpiles[min(plpiles)]['qty'] -= 1

                if plpiles[min(plpiles)] == 0:
                    del plpiles[min(plpiles)]

        elif action == 'destroy':
            if (noun == 'rationed' or
                    noun == 'unrationed' or
                    noun == 'produce supplies' or
                    noun == 'antiviral lab'):
                pldeck[noun] -= 1
            else:  # assume it is a city
                request_deck = True
                while request_deck:
                    deck_type = input('Player or Infection deck? ')
                    deck_type = deck_type.lower()
                    deck_type = deck_type.strip()

                    if deck_type == 'infection':
                        infdeck = city_verb(noun, 'discard', pldeck)
                        request_deck = False

                    elif deck_type == 'player':
                        pldeck = city_verb(noun, 'destroyed', pldeck)
                        request_deck = False

                    elif deck_type == 'end game':
                        print('Ending the game')
                        break

                    else:
                        print('Did not recognize the deck')

        elif (action == 'save' and
              noun == 'deck'):
            save_deck(infdeck, pldeck, plpiles)

        elif (action == 'open' and
              noun == 'deck'):
            infdeck, pldeck, plpiles = open_deck()

        elif (action == 'evaluate' and
              noun == 'deck'):
            evaluate_decks(infdeck, pldeck, plpiles)

        elif (action == 'end' and
              noun == 'game'):
            break

        else:
            print('Selected action has no function yet')

    elif (action == 'interupt'):
        pass

    elif (action =='exit'):
        break

    else:
        print('That is an unknown action, please try again.\n' +
              'Available commands are:\t')
        for x in cmd_list:
            print('\t' + x)
