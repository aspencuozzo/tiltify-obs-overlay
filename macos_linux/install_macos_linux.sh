#!/bin/bash
if python3 --version 2>&1 | grep -q '^Python 3\.'; then
    pyp="python3"
elif python --version 2>&1 | grep -q '^Python 3\.'; then
    pyp="python"
elif py --version 2>&1 | grep -q '^Python 3\.'; then
    pyp="py"
else
    printf "ERROR: Python 3 could not be found.\n"
    exit 1
fi

if ! $pyp -m pip install -r ../app/requirements.txt --break-system-packages; then
    printf "ERROR: There was an error installing required packages.\n"
    exit 1
fi

printf "\n"; read -rsn1 -p "The credentials file will now be opened for you to edit. Press any key to continue."

if ! nano ../app/credentials-example.json; then
    printf "ERROR: Could not open nano text editor.\n"
    exit 1
fi

mv ../app/credentials-example.json ../app/credentials.json
printf "\nAll set! To start the program, simply run $(tput bold)sh run_macos_linux.sh\n"
perl -i -l -p -e "print 'pyp=$pyp' if $. == 2" run_macos_linux.sh