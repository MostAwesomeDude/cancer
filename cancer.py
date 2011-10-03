import sys

port = int(sys.argv[-1])

from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site, NOT_DONE_YET
from twisted.internet.threads import deferToThread
from twisted.web.template import Element, XMLString, flatten, renderer

from twisted.python import log
log.startLogging(sys.stdout)

"""
This is a simple web application which, upon every request, politely greets
the user, gives them some statistics, then calculates a Fibonacci number
related to the number of current users requesting pages from this
application.

I wrote this application to prove a handful of points. Credit to glyph for
asking me to do this, and to Ted Dzuiba for being a dick on the Internets and
thus inspiring me to also be a dick on the Internets.
"""

def fibonacci(n):
    if n <= 0:
        return 0
    if n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)

class CancerElement(Element):

    loader = XMLString("""
        <html xmlns:t="http://twistedmatrix.com/ns/twisted.web.template/0.1">
            <head>
                <title>Cancer Demo</title>
            </head>
            <body>
                <h1>Cancer Demo</h1>
                <p>Hi there! I'm going to do a small dance for you. Are you
                ready? First, let's figure out how many threads are currently
                running. There are <span t:render="threads" /> running.</p>
                <p>Now, let's figure out a Fibonacci number. Ready? Here we
                go: <span t:render="fib" />. Whee!</p>
                <p>Thanks for being a good sport. Up from the start of the
                request until now, I estimate I've taken <span
                t:render="seconds" /> to handle your request. Aren't I a
                speedy worker? But, no matter what, I've not timed out. I just
                have been busy in the background with other tasks.</p>
            </body>
        </html>
    """)

    def __init__(self):
        self.timestamp = reactor.seconds()

    @renderer
    def threads(self, request, tag):
        count = reactor.getThreadPool().workers
        return tag("%d threads" % count)

    @renderer
    def fib(self, request, tag):
        count = reactor.getThreadPool().workers
        n = max(0, 40 - count)
        d = deferToThread(fibonacci, n)
        @d.addCallback
        def cb(result):
            return tag("%dth Fibonacci number is %d" % (n, result))
        return d

    @renderer
    def seconds(self, request, tag):
        elapsed = reactor.seconds() - self.timestamp
        return tag("%.4f seconds" % elapsed)

class CancerResource(Resource):

    isLeaf = True

    def render_GET(self, request):
        d = flatten(request, CancerElement(), request.write)
        @d.addCallback
        def flattened(none):
            request.finish()

        # Jumpstart page rendering.
        request.write(" " * 4096)
        request.write("<!DOCTYPE html>")
        return NOT_DONE_YET

reactor.listenTCP(port, Site(CancerResource()))
reactor.run()
