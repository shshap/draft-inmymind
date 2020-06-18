"""
inmymind is a platform that handles snapshots from your brain, so you
can keep track about your brain, and the most important, this comes from
the bottom of my heart - from now on, you won't forget anything! every moment of your
life is saved and available for you at any time!
for developers: you can choose the way that the system works, with a little
of effort, and very simply, you can add support on every protocol that you want.


The project is very consistent and coherent, once you understood one subpackage,
you understood everything. It has a very simple principle in the basis,
insert whatever tool you want, but follow the rules ans be consistent
with the names. Every subpackge acts the same, imports all the modules
based on their name and choose the one to use based in the configurations
or parameters if supplied.
For example, if the rabbitmq doesn't work, or simply you
don't like it, you can change the protocol between the server, the
parsers and the saver to be http for example, but make sure to write
all the needed functions/classes.
For the server, you would have to write a class Saver_http or specifically
Saver_flask (or any other name that you like, but it must start with Saver_),
that has a run method. In the kwargs for the run_saver method pass the
parameters you would like to have for __init__. Or you could simply write
a function if you do not need an entire class.

every part of the system I divided into two logics: getter and handler,
becuase they are completely decoupled. All the classes are drivers, and being
pulled by their names. I used the discovery method by urls to call the right
drivers. The program will call find the getter by the getter url, and then
the getter will find the right handler when he needs it, by the url. Moreover,
it also give the possibility for the getter to use different handlers throught
the time and depending on the data he got, and to not be bounded to a specific
handler, because that will make no sense because they are totally decoupled,
they do not need to know about each other.


protocol 'rabbitmq' with content format 'mind' is well defined:
the server send a json dict of the user to the saver, and to the parsers
send a path to file mind.gz with user_id and the raw snapshot (binary file).
the parser reads the file and send to saver a json object contains their
result. The saver then handles the data according to the handler url.

A basic assumption is that every component can get the data in any way and send it in any
way, and they do not have to be the same. And it also applies for the parsers.
That's the reason that every component has a getters pool and handlers pool, and
it chooses the appropriate getter/handler by the given url.
special case is the parser, that has a special logic inside it, which is more that just change
the format and etc. So it has getter, parser ans sender.
Also the client is like this, because it has a special logic inside it.
The server does not have a special logic (as we do not want it to have, because the goal is
to give it the minimum work as possible, since it already very busy accepting requests from many clients
and we want to prevent it being a bottle neck.

everything can be implemented with functions, and we also support classes, that contains a method
with a specific name that will be used. This method has to have url in his signature, for general support
reasons, but you can get the url also in the __init__ if one would like to inital the object with specific
parameters found in the url. So, both __init__ and the run method need to accept url as argument.
"""

import logging
from sys import stdout

root_logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stdout)
handler.setFormatter(logging.Formatter('%(module)s - %(message)s'))
root_logger.addHandler(handler)
root_logger.setLevel(logging.DEBUG)

logging.getLogger('pika').setLevel(logging.WARN)
