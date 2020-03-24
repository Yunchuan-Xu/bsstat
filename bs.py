import os
import json
import time
import requests
import hashlib

import pandas as pd
import matplotlib
from matplotlib import pyplot as plt

os.environ['TZ'] = 'Asia/Shanghai'
time.tzset()

matplotlib.use('Agg')

STAT_URL = r'https://brawlapi.cf/api/player?tag={}'
AUTH_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkaXNjb3JkX3VzZXJfaWQiOiIzNzA1MTA3MTkwODQ2NTg2ODgiLCJpYXQiOjE1NDk2MDM0NzN9.ci8gahtYn8ML96CmUHfRXr7Q12qm4NbfE8dOQSUkCiI'
UA_LIST = [
    r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    r'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19',
    r'Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
    r'Mozilla/5.0 (Linux; U; Android 2.2; en-gb; GT-P1000 Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
    r'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0',
    r'Mozilla/5.0 (Android; Mobile; rv:14.0) Gecko/14.0 Firefox/14.0',
    r'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36',
    r'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19',
    r'Mozilla/5.0 (iPad; CPU OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3',
    r'Mozilla/5.0 (iPod; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/3A101a Safari/419.3'
]
PLAYER_TAGS = ['2UUC9JRY', '22P9RRCG0', '282LJ8PQ2', '28C9LY0UY', '29Y0QLYUU', '29YY9YRP9', '2UJCP90GG', '2CY20RJPJ']
BRAWLER_NAMES = ['Shelly', 'Nita', 'Colt', 'Bull', 'Jessie', 'Brock', 'Dynamike', 'Bo',
                 'El Primo', 'Barley', 'Poco',
                 'Rico', 'Darryl', 'Penny', 'Carl',
                 'Piper', 'Pam', 'Frank',
                 'Mortis', 'Tara', 'Gene',
                 'Spike', 'Crow', 'Leon']
BRAWLER_ALIAS = {
    'Ricochet': 'Rico'
}
RANK_TABLE = {
    1: 0,
    2: 10,
    3: 20,
    4: 30,
    5: 40,
    6: 60,
    7: 80,
    8: 100,
    9: 120,
    10: 140,
    11: 160,
    12: 180,
    13: 220,
    14: 260,
    15: 300,
    16: 340,
    17: 380,
    18: 420,
    19: 460,
    20: 500
}


def now():
    return time.strftime('%Y-%m-%d %H:%M:%S')


def index2color(index):
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    return colors[index % len(colors)]


def skill_level(trophies, s_reference):
    normal_levels = ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D']
    if trophies < s_reference:
        normal_level_index = int(s_reference - trophies - 1) // 40
        if normal_level_index > len(normal_levels) - 1:
            normal_level_index = -1
        level = normal_levels[normal_level_index]
    else:
        high_level_index = int(trophies - s_reference) // 40
        if high_level_index:
            level = 'S+{}'.format(high_level_index)
        else:
            level = 'S'
    return level


class Player:
    @property
    def last_updated(self):
        return max(self.stats.keys())

    def __init__(self, tag, directory='', update=False):
        self.tag = tag
        self.directory = directory
        self.stats = dict()
        self.load_history_stats()
        if update:
            self.get_current_stat()
            self.save_stats()
        self.info = dict()
        self.add_info()
        self.print_stat_and_info(0)

    def __getitem__(self, name):
        if name in self.stats[self.last_updated]:
            result = self.stats[self.last_updated][name]
        elif name in self.info:
            result = self.info[name]
        else:
            result = None
        return result

    def __setitem__(self, name, value):
        self.info[name] = value

    def load_history_stats(self):
        path = os.path.join(self.directory, self.tag)
        if os.path.exists(path):
            with open(path) as f:
                self.stats = json.load(f)

    def get_current_stat(self):
        success = False
        tries = 0
        while True:
            r = requests.get(STAT_URL.format(self.tag), headers={'user-agent': UA_LIST[tries % len(UA_LIST)], 'Authorization': AUTH_KEY})
            try:
                stats = json.loads(r.content.decode())
                try:
                    tag = stats['tag']
                    if tag == self.tag:
                        self.stats[now()] = stats
                        break
                    else:
                        print('[{}] trial {} got stat with incorrect tag: {}'.format(now(), tries, tag))
                except Exception:
                    print('[{}] trial {} got unrecognized data: {}'.format(now(), tries, stats))
            except json.decoder.JSONDecodeError:
                print('[{}] trial {} request failed: {}'.format(now(), tries, r.content.decode()))
            tries += 1
            sleep_time = min(3600, tries * tries)
            print('[{}] sleep {}s...'.format(now(), sleep_time))
            time.sleep(sleep_time)

    def save_stats(self):
        with open(os.path.join(self.directory, self.tag), 'w') as f:
            f.write(json.dumps(self.stats))

    def add_info(self):
        self['brawlers_info'] = dict()
        for brawler_stat in self['brawlers']:
            brawler_info = {k: brawler_stat[k] for k in ('power', 'trophies')}
            brawler_info['skill_level'] = skill_level(brawler_info['trophies'], 100 + brawler_info['power'] * 40)
            self['brawlers_info'][brawler_stat['name']] = brawler_info
        total_powers = sum(map(lambda d: d['power'], self['brawlers_info'].values()))
        self['s_reference'] = 100 * self['brawlersUnlocked'] + total_powers * 40
        self['avg_skill_level'] = skill_level(self['trophies'] / self['brawlersUnlocked'], self['s_reference'] / self['brawlersUnlocked'])
        unlocked_brawlers = []
        for b in BRAWLER_NAMES:
            if b in self['brawlers_info']:
                unlocked_brawlers.append(b)
        self['unlocked_brawlers'] = unlocked_brawlers

    def print_stat_and_info(self, verbose=1):
        print('[{}] {} (updated at {})'.format(now(), self['name'], self.last_updated))
        if verbose:
            print('**** stat ****')
            print(json.dumps(self.stats[self.last_updated]))
            print('**** info ****')
            print(json.dumps(self.info))
            print()


def update_figures(update_player=True):
    print('[{}] getting players...'.format(now()))
    players = dict()
    for player_tag in PLAYER_TAGS:
        player = Player(player_tag, update=update_player)
        players[player['name']] = player

    print('[{}] processing...'.format(now()))
    update_times = []
    for player in players.values():
        update_times.extend(list(player.stats.keys()))
    initial_update_time = pd.Timestamp(min(update_times))
    latest_update_time = pd.Timestamp(max(update_times))
    right_margin = (latest_update_time - initial_update_time) / 10

    all_trophies = dict()
    for p, player in players.items():
        stats = player.stats
        brawler_trophies = dict()
        for t, stat in stats.items():
            brawler_trophies[t] = {BRAWLER_ALIAS.get(b['name'], b['name']): b['trophies'] for b in stat['brawlers']}
            brawler_trophies[t].update(dict(Total=stat['trophies']))
        df = pd.DataFrame(brawler_trophies).T
        df = df[['Total'] + player['unlocked_brawlers']]
        df.index = pd.to_datetime(df.index)
        all_trophies[p] = df.sort_index()

    print('[{}] plotting by_player.png'.format(now()))
    plt.figure(figsize=(15, (len(players) + 1) // 2 * 5))
    i = 0
    for p, player in players.items():
        i += 1
        plt.subplot(((len(players) + 1) // 2), 2, i)
        plt.title(p)
        for b in all_trophies[p].columns[1:]:
            brawler_info = player['brawlers_info'][b]
            color = index2color(BRAWLER_NAMES.index(b))
            trophies_series = all_trophies[p][b]
            plt.plot(trophies_series,
                     label='{} (Power {}, {})'.format(b, brawler_info['power'], brawler_info['skill_level']),
                     color=color)
            t, v = trophies_series.index[-1], trophies_series[-1]
            plt.plot(t, v,
                     color=color,
                     marker='o')
            plt.text(t + right_margin * 0.2, v, str(int(v)), ha='left', va='center', fontsize=10, color=color)
        plt.xlim(initial_update_time, latest_update_time + right_margin)
        plt.ylim(bottom=0)
        plt.legend(loc='upper left', prop={'size': 8})
    plt.tight_layout(pad=2)
    plt.suptitle('updated at {}'.format(now()), y=1)
    plt.savefig('by_player.png')
    plt.close()
    print('[{}] by_player.png updated'.format(now()))

    print('[{}] plotting by_brawlers.png'.format(now()))
    plt.figure(figsize=(15, (len(BRAWLER_NAMES) + 2) // 2 * 5))
    i = 1
    plt.subplot((len(BRAWLER_NAMES) // 2 + 1), 2, i)
    plt.title('Total (with S-Reference & Avg. Skill Level)')
    for p, player in players.items():
        color = index2color(list(players.keys()).index(p))
        trophies_series = all_trophies[p]['Total']
        plt.plot(trophies_series,
                 label='{} ({}, {})'.format(p, player['s_reference'], player['avg_skill_level']),
                 color=color)
        t, v = trophies_series.index[-1], trophies_series[-1]
        plt.plot(t, v,
                 color=color,
                 marker='o')
        plt.text(t + right_margin * 0.2, v, str(int(v)), ha='left', va='center', fontsize=10, color=color)
    plt.xlim(initial_update_time, latest_update_time + right_margin)
    plt.ylim(bottom=0)
    plt.legend(loc='upper left', prop={'size': 8})
    for b in BRAWLER_NAMES:
        i += 1
        plt.subplot((len(BRAWLER_NAMES) // 2 + 1), 2, i)
        plt.title(b)
        for p, player in players.items():
            if b in all_trophies[p]:
                brawler_info = player['brawlers_info'][b]
                color = index2color(list(players.keys()).index(p))
                trophies_series = all_trophies[p][b]
                plt.plot(trophies_series,
                         label='{} (Power {}, {})'.format(p, brawler_info['power'], brawler_info['skill_level']),
                         color=color)
                t, v = trophies_series.index[-1], trophies_series[-1]
                plt.plot(t, v,
                         color=color,
                         marker='o')
                plt.text(t + right_margin * 0.2, v, str(int(v)), ha='left', va='center', fontsize=10, color=color)
        plt.xlim(initial_update_time, latest_update_time + right_margin)
        plt.ylim(bottom=0)
        plt.legend(loc='upper left', prop={'size': 8})
    plt.tight_layout(pad=2)
    plt.suptitle('updated at {}'.format(now()), y=1)
    plt.savefig('by_brawler.png')
    plt.close()
    print('[{}] by_brawler.png updated'.format(now()))


if __name__ == '__main__':
    update_figures()
    while True:
        print()
        print('update in 1h...', end='\r')
        time.sleep(40)
        for i in range(59):
            print('update in {}min... '.format(59-i), end='\r')
            time.sleep(60)
        update_figures()
