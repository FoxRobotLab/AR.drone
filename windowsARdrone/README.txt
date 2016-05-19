There's a fair bit of POSIX-specific code in the original drone code.
Many of the files are identical. The modified files are:

libardrone.py
arnetworkq.py (replaces arnetwork.py)
FoxDemo.py
h264decoder.py


-------------

SUMMARY OF CHANGES: (h264decoder includes debug tips for if ffmpeg isn't 
working)

libardrone.py
Originally used a pipe to deliver a kill signal to arnetwork. This is 
efficient on POSIX systems since select() monitors whether or not the pipe
has been written to. But it implements the select() syscall, and on 
Windows it uses the WinSock library instead, which handles sockets but not
pipes. The only method I could find for checking a pipe was blocking, so
the options were send a queue instead (which has the non-blocking method
q.get_nowait()) or do some gross things with timed processes. Queues it 
was.

arnetworkq.py (summary of changes from arnetwork.py)
As above: changed the pipe to a queue. Removed the pipe from the select()
call, since it is not a socket and so doesn't work on Windows. Removed the
now-useless code which assumed that select() might say the pipe was ready
to be read. Handled queue input stopping the while loop.

h264decoder.py
This file implements a version of which, a unix command. It looks through
your PATH and tries to find something called 'ffmpeg' in one of those
directories. This will always fail - you must search for 'ffmpeg.exe' 
instead. Windows has no dev/null so that's switched out for NUL.
On Windows, the Popen command cannot take a method for process termina-
tion. Remove it. This is not ideal, as ffmpeg will not close automatic-
ally. The two kill functions are now dead code, but I left them there.
Last change is removing the first two options of Popen, which regarded
nice values.

FoxDemo.py
Added self.drone.halt(), line 29. This tells libardrone to end misc 
running processes.