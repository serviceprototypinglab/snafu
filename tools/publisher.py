# Syntax: python3 publisher.py amqp://guest:guest@localhost:6379/

from kombu import Connection
import datetime
import sys

with Connection(sys.argv[1]) as conn:
    try:
      simple_queue = conn.SimpleQueue('sslq')
    except:
      print('Error: connection to broker or queue failed.')
      exit()
    message = 'helloword, sent at %s' % datetime.datetime.today()
    simple_queue.put(message)
    print('Sent: %s' % message)
    simple_queue.close()
