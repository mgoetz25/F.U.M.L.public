This is where the test scripts are located.
Each script should test a specific functionality via some testing framework or library like [unittest](https://docs.python.org/3/library/unittest.html#module-unittest).
The idea is that a driver script in the /src directory will recursivly iterate through all of the scripts in this directory and execute them individually.
