# 11 - Capstone: a TCP echo server (spec only, no scaffolding)

Everything before this was a drill. This is the first exercise where you design
something, and it is the last step before your HTTP server.

## Build

A TCP echo server on `localhost:9999` using asyncio's **streams** API.

1. Accept connections. Read a line, write it back, repeat until the peer
   disconnects. Close cleanly on either side hanging up.
2. Print a line on connect and disconnect, including the peer address, so you
   can watch overlap happen.
3. Handle a client that connects and then says nothing for a minute without
   affecting anybody else.
4. Drop a connection that has been idle for 10 seconds, and say so in the log.
5. Ctrl-C shuts down: stop accepting, let in-flight writes finish, close every
   open connection, print a summary of how many you served.

## Verify

```
nc localhost 9999          # in two or three terminals at once
```

Type in one, get it back. Then: connect from three terminals, type into the
*third* one only. If the first two are blocking it, you have rebuilt the exact
bug in your HTTP server. Then open a connection and type nothing - the others
must stay responsive. Then leave one idle for 10 seconds and watch it drop.

Requirement 5 is the one that will teach you the most, and the one most
tutorials skip.

## Questions to answer for yourself before moving on

- Where in your design does the accept loop hand off, and what would happen if
  it awaited the handler inline instead? Try it. Confirm it breaks. That is the
  mistake you were warned about, and you should see it with your own eyes once.
- The reader object handles buffering for you. What happens if a client sends
  half a line and pauses - who is holding that partial data, and where?
- If a client sends 10 MB with nothing reading it, who buffers it, and what
  stops that from being unbounded?
- On Ctrl-C, which exception arrives where, and what cancels the connection
  tasks? What did the task group do for you here for free?

## Then: the bridge to your HTTP server

Do not port yet. First answer these about the code in `app/` of
`~/repos/codecrafters-http-server-python`:

1. `Server.serve_forever` has one accept loop and one blocking `recv`. Which
   line becomes an await, and which line becomes a spawn?
2. `Request.__init__` takes `data: bytes` from a single `recv(1024)` and assumes
   it received a whole request. Streams give you a reader instead. What is the
   right read call for "read until the end of the headers", and where does the
   body come from after that? (You need this for the POST stage regardless of
   whether you go async - the current code is already technically wrong.)
3. `Router`, the routes, `Request`, `Response`: which of these need to become
   `async def`? Justify each answer. The correct number is smaller than it
   looks, and exercise 07 tells you why.
4. Your `except Exception` in the accept loop: after exercise 05, what does it
   now catch and, more importantly, what does it correctly *not* catch?

When you can answer all four, the port is mostly typing.
