import os
import re
import time

from config import *
from cities import coordinates
from webhook import execute

sent_messages_file = os.path.join(os.path.dirname(DAYZSERVER_X64_ADM), 'sent_messages.txt')

print('[*] Killfeeding discord...')


def parse(line):
    line = line.strip()
    pos_pattern = r'pos=<(.+?)>'
    pos_found = re.findall(pos_pattern, line)
    closest_location = None
    if pos_found:
        dist = lambda x, y: (x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2
        position = pos_found[0]
        position = position.split(',')
        position = [item.strip() for item in position]
        position = [float(item) for item in position]

        _coordinates = [coord[0] for coord in coordinates]
        closest = min(_coordinates, key=lambda co: dist(co, (position[0], position[1])))
        for coord in coordinates:
            if closest == coord[0]:
                closest_location = coord[1]

    pattern = r'\(.+?\)'
    line = re.sub(pattern, "", line)

    line = re.sub('Zmb.*$', "um infectado", line)  # <= comment to keep in english

    line = line.replace('killed by', 'morto por')  # <= comment to keep in english
    line = line.replace('with', 'com um(a)')  # <= comment to keep in english
    line = line.replace('"', '**')
    line = line.replace('Player', '')
    line = line.replace('from', 'a')  # <= comment to keep in english
    line = line.replace('meters', 'metros')  # <= comment to keep in english
    if closest_location:
        return ' '.join(line.strip().split()) + ' perto de %s' % closest_location
        # return ' '.join(line.strip().split()) + ' near %s' % closest_location <= english
    else:
        return ' '.join(line.strip().split())


if __name__ == '__main__':

    while True:
        try:
            fp = open(DAYZSERVER_X64_ADM, 'r')
            lines = fp.readlines()
            lines = [line.strip() for line in lines]
            fp.close()

            fp = open(sent_messages_file, 'r')
            sent_messages = fp.readlines()
            sent_messages = [message.strip() for message in sent_messages]
            fp.close()

            for line in lines:

                if line in sent_messages:
                    continue

                if not 'killed' in line:
                    continue

                if 'SurvivorF_' in line or 'SurvivorM_' in line:
                    continue

                msg = parse(line)
                print(msg)

                if msg:
                    execute(DISCORD_WEBHOOK_URL, msg)

                    with open(sent_messages_file, 'a') as fp2:
                        fp2.write(line + '\n')
                        sent_messages.append(line)

        except Exception as E:
            print(E)
            time.sleep(30)
        time.sleep(10)
