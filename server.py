import sys
import socket
import threading
import time
import json
import glob
import os
import uuid

# Local Imports
from client import Client
from channel import Channel
import errorcodes


class Server:

    '''
    Server class. Opens up a socket and listens for incoming connections.
    Every time a new connection arrives, it creates a new Client thread
    object and defers the processing of the connection to it.
    '''

    def __init__(self):
        self.CONFIG = self.load_config()
        self.sock = None
        self.clients = []
        self.users = {}
        self.opers = []
        self.ips = []
        self.channels = self.load_channels()
        print(self.CONFIG)
        self.channels[self.CONFIG["SERVER_ADMIN_CHANNEL"]] = Channel(self,
            self.CONFIG["SERVER_ADMIN_CHANNEL"], {"O": True, "p": True}, "Server Admin Channel")

    def rehash(self):
        """
        Reloads the config and channels
        """
        self.channels = self.load_channels()
        self.CONFIG = self.load_config()

    def load_config(p="./config.json"):
        """
        Parse the config file and set default values for
        anything missing
        """
        config = json.load(open("./config.json", 'r'))
        charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return {
            "ADDRESS": config.get("ADDRESS", "127.0.0.1"),
            "BANLIST": config.get("BANLIST", "banlist.txt"),
            "CHAN_BADWORD_LIMIT": int(config.get("CHAN_BADWORD_LIMIT", 50)),
            "CHAN_BAN_LIMIT": int(config.get("CHANNEL_BAN_LIMIT", 50)),
            "CHAN_TOPIC_LIMIT": int(config.get("CHAN_TOPIC_LIMIT", 300)),
            "CHANNEL_CREATION": config.get("CHANNEL_CREATION", False),
            "DEFAULT_CHAN_FLAGS": list(config.get("DEFAULT_CHAN_FLAGS", "n")),
            "CONNECTION_LIMIT": int(config.get("CONNECTION_LIMIT", 5)),
            "DEFUALT_OPER_FLAGS": list(config.get("DEFAULT_OPER_FLAGS", "kw")),
            "I:LINES": config.get("I:LINES", "ilines.txt"),
            "MAX_CHAN_NAME_LENGTH": int(config.get("MAX_CHAN_NAME_LENGTH", 20)),
            "MAX_NICK_LENGTH": int(config.get("MAX_NICK_LENGTH", 12)),
            "MAX_RECV_SIZE": int(config.get("MAX_RECV_SIZE", 2048)),
            "NICK_CHAR_SET": config.get("NICK_CHAR_SET", charset),
            "OPER_VHOST": config.get("OPER_VHOST", "server/admin"),
            "PORT": int(config.get("PORT", 5050)),
            "RESERVED_NICKS": config.get("RESERVED_NICKS", []),
            "SERVER_ADMIN_CHANNEL": config.get("SERVER_ADMIN_CHANNEL", "&ADMIN"),
            "SERVER_MAX_USERS": int(config.get("SERVER_MAX_USERS", 100)),
            "TIMEOUT": config.get("TIMEOUT", 0.5),
        }

    def load_channels(self):
        """
        Looks in the channel folder for channel json files
        and creates channels based of that information
        """
        channels = {}
        for c in glob.glob("channels/*.json"):
            try:
                channel = json.load(open(c, 'r'))
                channels[channel["name"]] = Channel(self,
                    channel.get("name", "Unknown"), channel.get("flags", {}),
                    channel.get("topic", ""), channel.get("banlist", []),
                    channel.get("ops", []), channel.get("owner", ""),
                    channel.get("badwords", []), channel.get("public_notes", ""),
                    channel.get("op_notes", ""))
                print("Loaded channel %s from %s" % (channel["name"], c))
            except:
                print("Failed to load channel json %s" % c)
        return channels

    def get_account(self, nick):
        """
        Returns the account of `nick`
        """
        if os.path.exists("accounts/%s.json" % nick):
            return json.load(open("accounts/%s.json" % nick))

    def get_ilines(self):
        with open(self.CONFIG["I:LINES"], 'r') as f:
            for line in f.readlines():
                yield line.split()[0]

    def register_client(self, client):
        # if the server is full tell the client and disconnect them
        if len(self.clients) >= self.CONFIG["SERVER_MAX_USERS"]:
            client.writeline(json.dumps({
                "type": "SERVERFULL"
            }))
            client.quit()
            return False
        # if too many connections from this IP disconnect client
        # if the client doesn't have an I:Line
        if not client.ip in self.get_ilines():
            # See if IP breaks connection limit
            if (self.ips.count(client.ip) + 1) > self.CONFIG["CONNECTION_LIMIT"]:
                client.writeline(json.dumps({
                    "type": "SERVERMSG",
                    "message": "Too many connections from this IP"
                }))
                client.quit()
                return False
        # if this client is banned tell them to GTFO and disconnect them
        if client.ip in [ip.strip() for ip in open(self.CONFIG["BANLIST"], 'r').readlines()]:
            self.writeline("%s is banned." % (client.ip))
            client.writeline(
                json.dumps({"type": "YOUSERVERBANNED"}))
            client.quit()
            return False
        else: # let the clinet on the server
            self.users[client.nick] = client
            self.ips.append(client.ip)
            self.writeline("%s is registered as %s" % (client.ip, client.nick))
            if os.path.exists("motd.txt"):
                for line in open("motd.txt", 'r').readlines():
                    client.writeline(json.dumps({
                        "type": "SERVERMOTD",
                        "message": line.strip("\n")
                    }))
            client.writeline(json.dumps({
                "type": "SERVERCONFIG",
                "config": self.CONFIG
            }))
            client.writeline(json.dumps({
                "type": "SERVERUSERS",
                "amount": len(self.clients)
            }))
            return True

    def register_account(self, client, email, hashedpw):
        if os.path.exists("accounts/%s.json" % client.nick):
            client.writeline("This nick is already registered.")
            client.writeline(json.dumps({
                "type": "ERROR",
                "code": errorcodes.get("nick already registered"),
                "message": "Nick is already registered"
            }))
        else:
            with open("accounts/%s.json" % client.nick, 'w') as f:
                f.write(json.dumps({
                    "email": email,
                    "password": hashedpw,
                    "notes": [],
                    "uuid": client.nick + ':' + str(uuid.uuid4()),
                    "time_registered": int(time.time())
                }, sort_keys=True, indent=4, separators=(',', ': ')))
            self.writeline(
                "%s created a new account [%s]" % (client.ip, client.nick))
            client.writeline(json.dumps({
                "type": "SERVERMSG",
                "message": "Your nick is now registered! You can now login with `login <password>`"
            }))

    def client_login(self, client, hashedpw):
        if os.path.exists("accounts/%s.json" % client.nick):
            user = json.load(open("accounts/%s.json" % client.nick, 'r'))
            if hashedpw == user["password"]:
                client.account = user
                client.writeline(json.dumps({
                    "type": "SERVERMSG",
                    "message": "You're now logged in!"
                }))
                self.writeline("%s logged in" % client.nick)
                client.on_login()
            else:
                client.writeline("ERROR Invalid password for %s" % client.nick)
                client.writeline(json.dumps({
                    "type": "ERROR",
                    "code": errorcodes.get("invalid nick password"),
                    "message": "invalid password for %s" % client.nick
                }))
                self.writeline("%s failed to login" % client.nick)
        else:
            client.writeline(json.dumps({
                "type": "ERROR",
                "code": errorcodes.get("invalid account name"),
                "message": "account %s not found." % client.nick
            }))

    def oper(self, client, hashedpw):
        """
        Turns the client into an oper (Server Operator)
        """
        self.writeline("%s used the oper command" % client.ip)
        oper_blocks = [op.strip()
                       for op in open("./opers.txt", "r").readlines()]
        if client.ip + '|' + hashedpw in oper_blocks:
            if self.CONFIG["OPER_VHOST"]:
                client.ip = self.CONFIG["OPER_VHOST"]
            client.add_flag('O')
            client.add_flags(self.CONFIG["DEFUALT_OPER_FLAGS"])
            client.writeline(json.dumps({
                "type": "SERVERMSG",
                "message": "You are now an oper!"
            }))
            client.join(self.CONFIG["SERVER_ADMIN_CHANNEL"])
            self.writeline("%s oppered" % client.nick)
            self.opers.append(client)
        else:
            client.writeline(json.dumps({
                "type": "SERVERMSG",
                "message": "invalid oper credentials"
            }))
            self.writeline("%s failed to oper" % client.nick)

    def oper_message(self, client, message):
        """
        Sends a message to all opers with `w` flag
        """
        for oper in self.opers:
            if 'w' in oper.flags:
                oper.writeline(json.dumps({
                    "type": "OPERMSG",
                    "nick": client.nick,
                    "message": message
                }))

    def global_message(self, message):
        """
        Send a message to all clients connected to the server
        """
        for client in self.clients:
            client.writeline(json.dumps({
                "type": "SERVERMSG",
                "message": "ANNOUNCEMENT: " + message
            }))

    def client_whois(self, client, nick):
        if self.users.get(nick):
            self.users[nick].on_whois(client)
            self.writeline("%s used whois on %s" % (client.nick, nick))
        else:
            client.writeline(json.dumps({
                "type": "ERROR",
                "code": errorcodes.get("invalid channel/nick"),
                "message": "%s isn't on the server" % client.nick
            }))

    def create_channel(self, client, name, flags={}, topic=""):
        name = name[0:self.CONFIG["MAX_CHAN_NAME_LENGTH"]]
        if name.strip().startswith("#"):
            if name not in self.channels.keys():
                self.channels[name] = Channel(self, name, flags, topic)
                self.channels[name].save()
                self.writeline("%s created a new channel %s" % (client.nick, name))
                return True
            else:
                client.writeline(json.dumps({
                    "type": "SERVERMSG",
                    "message": "Channel %s is already created" % name
                }))
        else:
            client.writeline(json.dumps({
                "type": "SERVERMSG",
                "message": "invalid channel name "
            }))


    def ban_ip(self, ip):
        """
        Ban a ip from joining the server
        """
        with open("banlist.txt", 'a') as f:
            f.write(ip + "\n")
        self.writeline("Added %s to banlist.txt" % ip)

    def set_motd(self, motd):
        """
        Sets the message of the day
        """
        with open("motd.txt", 'w') as f:
            f.write(motd)

    def writeline(self, message):
        print(message)
        self.channels[self.CONFIG["SERVER_ADMIN_CHANNEL"]].writeline(json.dumps({
            "type": "CHANMSG",
            "channel": self.CONFIG["SERVER_ADMIN_CHANNEL"],
            "nick": "SERVER",
            "message": message
        }))

    def channel_list(self, client):
        """
        Sends a list of all public channels to the client
        Sends a list of all channels to a client that is an oper
        """
        chans = []
        for chan in self.channels:
            # if the channel is not private
            if not self.channels[chan].flags.get('p'):
                chans.append(chan)
            elif client.is_oper():  # opers can see all channels
                chans.append(chan)
        client.writeline(json.dumps({
            "type": "CHANLIST",
            "channels": chans
        }))

    def run(self):
        '''
        Server main loop.
        Creates the server (incoming) socket, and listens on it of incoming
        connections. Once an incomming connection is deteceted, creates a
        Client to handle it, and goes back to listening mode.
        '''
        all_good = False
        try_count = 0
        # Attempt to open the socket
        while not all_good:
            if try_count > 3:
                # Tried more than 3 times, without success... Maybe the port
                # is in use by another program
                sys.exit(1)
            try:  # Create the socket
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # Bind it to the interface and port we want to listen on
                self.sock.bind((self.CONFIG["ADDRESS"], self.CONFIG["PORT"]))
                # Listen for incoming connections. This server can handle up to
                # 5 simultaneous connections
                self.sock.listen(50)
                all_good = True
                break
            except socket.error, err:
                # Could not bind on the interface and port, wait for 10 seconds
                print 'Socket connection error... Waiting 10 seconds to retry.'
                del self.sock
                time.sleep(10)
                try_count += 1

        print ("`telnet %s %s`" %
               (self.CONFIG["ADDRESS"], self.CONFIG["PORT"]))

        try:
            while True:
                try:
                    self.sock.settimeout(0.5)  # .5 second timeout
                    client_sock = self.sock.accept()[0]
                except socket.timeout:
                    # No connection detected, sleep for one second, then check
                    time.sleep(1)
                    continue
                # Create the Client object and let it handle the incoming
                # connection
                try:
                    client = Client(client_sock, self)
                    if self.register_client(client):
                        self.clients.append(client)
                        client.start()
                    # Go over the list of threads, remove those that have finished
                    # (their run method has finished running) and wait for them
                    # to fully finish
                    self.users = {}
                    for client in self.clients:
                        if not client.isAlive():
                            self.clients.remove(client)
                        else:
                            self.users[client.nick] = client
                except Exception, err:
                    print("Client error: %s" % err)

        except KeyboardInterrupt:
            print 'Ctrl+C pressed... Shutting Down'
            quit()
        except Exception, err:
            print 'Exception caught: %s\nClosing...' % err
            quit()
        # Clear the list of threads, giving each thread 1 second to finish
        # NOTE: There is no guarantee that the thread has finished in the
        #    given time. You should always check if the thread isAlive() after
        #    calling join() with a timeout paramenter to detect if the thread
        #    did finish in the requested time
        #
        for client in self.clients:
            client.join(1.0)
        # Close the socket once we're done with it
        self.sock.close()
