# 0.1.22
## Done
### Faster update_variable_dictionary
## In Progress
## Not Started
### Multiple tag reads
### Variable List Enhancement
Many programmers want to have access to the lists of variables that are stored in the CIPDispatcher. I use them to 
make read_variable and write_variable methods in the higher level NSeries know how to pack and unpack data, but others
are using them to see available tags in the controller.

This enhancement will expose user and system variables more usefully in the actual NSeries class. 
There will be separate methods as reading the data type and structure of a variable and 
reading the contents of a variable are separate CIP messages and update_variable_dictionary 
is already a very expensive method in terms of network messages. 

Actually reading the contents of all variables should be something the programmer explicitly requests, 
otherwise network traffic for folks that just wanted to know variable names and did not want to retrieve 
the contents at the same time would be excessive.