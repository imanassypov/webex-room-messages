import requests
import sys, argparse

argv = sys.argv[1:]

parser=argparse.ArgumentParser()
parser.add_argument("--room", help="Name of Webex room to collect messages from", required=True)
parser.add_argument("--file", help="File to write collected messages to", required=True)
parser.add_argument("--key", help="Webex API Key", required=True)
args=parser.parse_args()


WEBEX_API="https://webexapis.com/v1/"

WEBEX_ROOMNAME=args.room
FILE_OUT=args.file
WEBEX_KEY=args.key

webex_session = requests.Session()
webex_headers={"Authorization": "Bearer " + WEBEX_KEY}
webex_session.headers.update(webex_headers)


def get_room_id (webex_rooms_json, room_name):
    room_id = None
    for room in webex_rooms_json["items"]:
        if room["title"] == room_name:
            room_id = room["id"]
            break
    return room_id

def get_messages (room_id):
    webex_messages=None
    if room_id is not None:
        webex_messages = webex_session.get(url=WEBEX_API+"messages?roomId={}".format(room_id))
    return webex_messages.json()

def dump_to_file(webex_messages, filename):
    with open(filename, 'w') as f:
        f.write(str(webex_messages['items']))

webex_rooms = webex_session.get(url=WEBEX_API+"rooms")
if webex_rooms.status_code != 200:
    print ("invalid API key, error code {}".format(webex_rooms.status_code))
    sys.exit()

room_id = get_room_id(webex_rooms.json(), WEBEX_ROOMNAME)
pages=0

while webex_rooms.headers.get('link') and room_id is None:
    link = (webex_rooms.headers['link']).split(';')[0][1:-1]
    webex_rooms =  webex_session.get(url=link)
    room_id = get_room_id(webex_rooms.json(), WEBEX_ROOMNAME)
    pages += 1
    print('searching page: {} link {}'.format(pages, link))

webex_messages = get_messages(room_id)

dump_to_file(webex_messages, FILE_OUT)

print ('wrote {} messages to file {}'.format(len(webex_messages['items']), FILE_OUT))