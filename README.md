# puppymage

### Run in Windows

py -3 -m venv env\
env\scripts\activate\

### TODO

 * Proper logging
 * Set description on the jpeg
 * Exclude patterns file
 * Export results to file and import them on load
 * DSL with parsimonious (PEG):

    go "url"
    wait "selector"
    click "selector"
    upload "selector"
    select "selector" -> while
        image "selector"
        press "key"
        sleep 1 10