Before running the program, the following libraries and technology are required:

- Python 3.10 or higher
    - networkx
    - pika

- Docker
- RabbitMQ 

Running the program

1. Create a RabbitMQ docker container with the following command:

docker run --name mqserver -p 5672:5672 rabbitmq

2. (Optional) Modify the configurations files following the format below:

RCID ASN
No. of RCs connected
RCID ASN Mbps $/Mbps
(repeat for # of RCs)
No. of DCs connected
DC# Mbps $/Mbps
(repeat for # of DCs)

3. Open X terminals and run the program using the command:

python3 main.py X (where X is the RCID)


