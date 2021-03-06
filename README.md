# AwwRC
Because IRC didn't have enough Aww

## How to use!
Start the server: `python2 main.py`

Connect with a client: `telnet 127.0.0.1 5050`
NOTE: telnet will not work on windows. use putty with unix line endings enabled

### Channel Flags
- n: No outside messages allowed
- k: Password protected channel
- l: Limits the amount of users
- O: Server operators only
- F: Redirects users to another channel
- p: Prevents the channel from showing in the public list
- G: Enabled bad word list
- P: Playback - Sends the last x lines to a new client joining the channel
- B: prevents clients with the `B` (bot flag) from joining
- R: Only registered clients can join

### User Flags
- O: Server Operator/Server Admin/Oper
- B: Flags the client as a bot
- w: Allows the client to receive oper messages
- i: Prevents the user from showing up on server user list (not implemented)
- a: Marks the client as away

### Commands
- quit: `quit <message>` disconnects you from the server
- nick: `nick <nick>` changes your nick
- usernote: `usernote <nick> <message>` leave a note for a registered user while they're away
- userflag: `userflag <add/remove> <flag>` add or remove a flag from yourself
- chanlist: `chanlist` returns a list of all public channels (all channels if client is an oper)
- register: `register <password> <email>` create a new account on the server
- login: `login <password>` login to your account
- usermsg: `usermsg <nick> <message>` send a priavte message to another client on the server
- whois: `whois <nick>` gives you information on a client
- chanjoin: `chanjoin <channel> [password]` join a channel
- chanpart: `chanpart <channel> <message>` leave a channel
- chanmsg: `chanmsg <channel> <message>` send a message to a channel
- chankick: `chankick <channel> <nick> <reason>` removes a client from the channel **(chanop only)**
- chanflag: `chanflag <channel> <add/remove> <flag> <args>` set a channel flag **(chanop only)**
- chanban: `chanban <channel> <nick>` ban a client from the channel **(chanop only)**
- chanunban: `chanunban <channel> <ip>` unban an IP from the channel **(chanop only)**
- chanregister: `chanregister <channel>` registers a channel to you
- chanbadword: `chanbadword <channel> <add/remove> <word>` prevents clients from sending that *word* to the channel **(chanop only)**
- chanclientflag: `chanclientflag <channel> <add/remove> <nick> <flag>` sets a flag on client in a channel **(chanop only)**
- chanusers: `chanusers <channel>` returns a list of all users in that channel
- oper: `oper <password>` turns the client into an oper
- kill: `kill <nick>` removes a client from the server **(oper only)**
- sanick: `sanick <nick> <newnick>` forcfully change a clients nick **(oper only)**
- sajoin: `sajoin <nick> <channel>` forcefully joins a client into a channel **(oper only)**
- sapart: `sapart <nick> <channel>` forcefully removes a client from a channel **(oper only)**
- serverban: `serverban <IP>` bans an IP from the server **(oper only)**
- globalmsg: `globalmsg <message>` sends a message to all clients connected to the server **(oper only)**
- opermsg: `opermsg <message>` sends a message to all opers connected **(oper only)**

###Events Examples
#####*CHANJOIN*
```json
{
    "type": "CHANJOIN",
    "channel": "#example",
    "nick": "example",
    "ip": "127.0.0.1"
}
```
#####*CHANTOPIC*
```json
{
    "type": "CHANTOPIC",
    "channel": "#example",
    "topic": "this is a topic"
}
```
#####*CHANUSERS*
```json
{
    "type": "CHANUSERS",
    "channel": "#example",
    "topic": ["aww", "mike", "Pual"]
}
```
#####*SERVERMSG*
```json
{
    "type": "SERVERMSG",
    "message": "example message"
}
```
#####*CHANERROR*
```json
{
    "type": "CHANERROR",
    "channel": "#example",
    "message": "desc of error"
}
```
#####*YOUCHANBANNED*
```json
{
    "type": "YOUCHANBANNED",
    "channel": "#example",
}
```
#####*CHANPART*
```json
{
    "type": "CHANPART",
    "channel": "#example",
    "nick": "nilly",
    "ip": "127.0.0.1",
    "message": "bye bye!"
}
```
#####*CHANKICK*
```json
{
    "type": "CHANKICK",
    "channel": "#example",
    "nick": "nilly",
    "message": "Bad word"
}
```
#####*CHANBAN*
```json
{
    "type": "CHANBAN",
    "channel": "#example",
    "nick": "nilly",
}
```
#####*CHANUNBAN*
```json
{
    "type": "CHANUNBAN",
    "channel": "#example",
    "ip": "127.0.0.1",
}
```
#####*YOUCHANBANNED*
```json
{
    "type": "YOUCHANBANNED",
    "channel": "#example",
    "message": "Bad word!",
}
```
#####*CHANMSG*
```json
{
    "type": "CHANMSG",
    "channel": "#example",
    "message": "Hey, Everyone!",
    "nick": "nilly",
    "ip": "127.0.0.1"
}
```
#####*CHANFLAG*
```json
{
    "type": "CHANFLAG",
    "channel": "#example",
    "nick": "nilly",
    "operator": "Aww",
    "flag": "+o"
}
```
#####*NICK*
```json
{
    "type": "NICK",
    "old_nick": "cookies",
    "new_nick": "bobby"
}
```
#####*ERROR*
```json
{
    "type": "ERROR",
    "code": "003",
    "message": "invalid channel/nick"
}
```
#####*PICKNICK*
```json
{
    "type": "PICKNICK"
}
```
#####*INVALIDCOMMAND*
```json
{
    "type": "INVALIDCOMMAND"
}
```
#####*YOUQUIT*
```json
{
    "type": "YOUQUIT",
    "message": "rage quit :("
}
```
#####*YOUJOIN*
```json
{
    "type": "YOUJOIN",
    "channel": "#example"
}
```
#####*YOUPART*
```json
{
    "type": "YOUPART",
    "channel": "#example",
    "message": "bye bye!"
}
```
#####*YOUKICKED*
```json
{
    "type": "YOUKICKED",
    "channel": "#example",
    "message": "being silly"
}
```
#####*YOUKILLED*
```json
{
    "type": "YOUKILLED",
    "message": "bye bye!"
}
```
#####*YOUBANNED*
```json
{
    "type": "YOUBANNED",
    "channel": "#example"
}
```
#####*YOUSAJOINED*
```json
{
    "type": "YOUSAJOINED",
    "channel": "#example"
}
```
#####*YOUSAPARTED*
```json
{
    "type": "YOUSAPARTED",
    "channel": "#example"
}
```
#####*YOUSANICKED*
```json
{
    "type": "YOUSANICKED",
    "new_nick": "botbot"
}
```
#####*WHOIS*
```json
{
    "type": "WHOIS",
    "nick": "nilly",
    "message": "Logged In: True"
}
```
#####*NOTE*
```json
{
    "type": "NOTE",
    "from": "nilly",
    "message": "Hey dude! Message me you get this k?"
}
```
#####*USERMSG*
```json
{
    "type": "USERMSG",
    "nick": "nilly",
    "ip": "127.0.0.1",
    "message": "Hey dude! Message me you get this k?"
}
```
#####*SERVERFULL*
```json
{
    "type": "SERVERFULL"
}
```
#####*YOUSERVERBANNED*
```json
{
    "type": "YOUSERVERBANNED"
}
```
#####*SERVERMOTD*
```json
{
    "type": "SERVERMOTD",
    "message": "Welcome to AwwNet!"
}
```
#####*SERVERCONFIG*
```json
{
    "type": "SERVERCONFIG",
    "config": {"PORT": "127.0.0.1"}
}
```
#####*SERVERUSERS*
```json
{
    "type": "SERVERUSERS",
    "amount": 10
}
```
#####*OPERMSG*
```json
{
    "type": "OPERMSG",
    "nick": "Aww",
    "message": "Should we ban nilly?"
}
```
#####*CHANLIST*
```json
{
    "type": "CHANLIST",
    "channels": ["#Aww", "#programming", "#linux"]
}
```
