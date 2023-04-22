# Distributed Systems

This project was created to fulfill the requirements of the Distributed Systems course offered in the 9th semester at ECE NTUA. The objective of this assignment was to develop Noobcash, a straightforward cryptocurrency that can operate concurrently on a network of diverse nodes. The project is composed of the following components:

* A block class that defines the structure of blocks containing transactions.
* A blockchain class that defines the blockchain and maintains all the validated blocks.
* A wallet class that defines the wallet of each node in the network.
* Transaction classes that define a transaction and its status as either spent or unspent.

Moreover, each node in the network runs its own API and node instances that enable all the necessary functionalities of our system.  Furthermore, each node has its own CLI instance that allows the user to verify the node's balance, examine new transactions, and even scrutinize the transactions of the most recent block. The client interface of the bootstrap node also allows users to conduct basic experiments by running simultaneous transactions from all the nodes.



