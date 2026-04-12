Overview.

    Drift Checkers are made to help you find changes that stray from your baseline configuration, almost like a snapshot or saved state, but only to view what the configuration was. configuration monitoring is crucial to help prevent unauhorized changes to configs, this can be useful to stop attackers, or just to troubleshoot the network if there are issues.

Drift Types.

    there are 3 main types of drift,
    Missing is a key that existed originally, but not in the new config.
    Extra is a key that was added since the original config.
    Changed is a key that was modified since the original.

How Recursion Works.

    the compare_configs function uses recursion to dig all the way down a json file without needing to know how many elements it may include and can check all elements of dictionaries that it encounters.

DriftResult Class
    encapsulates each drift finding with an attribute and a method, examples of the results are shown below
Test Results
    === Drift Results ===
    [-] logging.destination (medium)
    [~] logging.enabled (high)
    [~] logging.level (low)
    [~] rules[0].port (low)
    [~] rules[1].source (low)
    [+] rules[2] (low)

    === Summary ===
    Total findings: 6
    High: 1, Medium: 1, Low: 4

Challenges
    Recursion was the biggest challenge, it is tough to wrap your head around when it needs to get called and not get it stuck in a loop. other than that, managing the diffirent data types in the json files was a challenge as well.

