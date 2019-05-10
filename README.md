# catm1_netwok.py
This python script creats SSH connection and run script on remote linux system (Nutaq). Script load Cat-m1 netwok on nutaq and unload netwok and close SSH connection after the execution time ends, given in parameters. 

- It is parameterized script, following are the parameters
	- host name
	- user name
	- password
	- mme_port
	- enb_port
	- executionTime (In minutes)
- Run script: Python catm1_nutaq_tcs.py 1.1.1.1 test test 98880 98881 10


# catm1_network_and_cellular_test.py
This python script creats SSH connection and run script on remote linux system (Nutaq). Script load Cat-m1 netwok on nutaq, after running cat-m1 netwok on nutaq script runs test cases on target board (C030_R410M) and when all test cases finined then unload netwok and close SSH connection.

- It is parameterized script, following are the parameters
	- host name
	- user name
	- password
	- mme_port
	- enb_port
	- test_command 
- Run script: Python catm1_nutaq_tcs.py 1.1.1.1 test test 98880 98881 ublox-at-cellular-interface-ext-TESTS-unit_tests-http

Note: BUILD needs to be there before running script. 
