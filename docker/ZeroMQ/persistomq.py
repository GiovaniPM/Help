import pathlib
import zmq
import persizmq

context = zmq.Context()
subscriber = context.socket(zmq.SUB)
subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
subscriber.connect("ipc:///some-queue.zeromq")

persistent_dir = pathlib.Path("/some/dir")
storage = persizmq.PersistentStorage(persistent_dir=persistent_dir)

def on_exception(exception: Exception)->None:
    print("an exception in the listening thread: {}".format(exception))

with persizmq.ThreadedSubscriber(
    callback=storage.add_message, subscriber=subscriber, 
    on_exception=on_exception):

    msg = storage.front()  # non-blocking
    if msg is not None:
        print("Received a persistent message: {}".format(msg))
        storage.pop_front()