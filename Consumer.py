import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)

# Receiving messages from the queue is more complex. It works by subscribing a callback function to a queue. Whenever we receive a message, this callback function is called by the Pika library. In our case this function will print on the screen the contents of the message.
def callback(ch, method, properties, body):
    print " [x] Received %r" % (body,)
    print("Doing work!")
    print " [x] Done\n\n"
    raw_input("Press Enter to continue...")
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Next, we need to tell RabbitMQ that this particular callback function should receive messages from our hello queue:
channel.basic_consume(callback,
                      queue='task_queue')

# Tells RabbitMQ not to give more than one message to a worker at a time
channel.basic_qos(prefetch_count=1)

# Start a never ending loop w8ting for a message
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()