# Short Range System Tests

Project for Short Range modules testing (BC310X, BX310X, BC127).

Structure of the repository:

    sr-system-tests\
        sr_framework         Short Range Test framework (Eddington, Euler, Melody).
        test_scripts         Test scripts (Generic and project specific test scripts).
        conftest.py          Example conftest.py - pytest configuration file.
        devices.json         Example devices configuration file.

## Running the tests
* Update conftest.py file based on your project configuration. Note that it must include the dut and remote fixtures.
* Update the devices.json file which includes the local device configuration.
* Run 'py -3 -m pytest -v -s' from the command line.
